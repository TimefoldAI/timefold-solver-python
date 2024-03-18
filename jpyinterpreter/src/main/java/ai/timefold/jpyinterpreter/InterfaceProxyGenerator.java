package ai.timefold.jpyinterpreter;

import java.lang.reflect.Modifier;
import java.util.Collections;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;

import ai.timefold.jpyinterpreter.implementors.JavaPythonTypeConversionImplementor;
import ai.timefold.jpyinterpreter.types.BuiltinTypes;
import ai.timefold.jpyinterpreter.types.PythonLikeType;
import ai.timefold.jpyinterpreter.util.MethodVisitorAdapters;
import ai.timefold.jpyinterpreter.util.arguments.ArgumentSpec;

import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.Type;

public class InterfaceProxyGenerator {
    /**
     * Generate an interface that just calls an existing instance of the interface.
     * Needed so Java libraries that construct new instances using the no-args
     * constructor use the correct instance of the function (the one with __closure__
     * and other instance fields).
     */
    public static <T> Class<T> generateProxyForFunction(Class<T> interfaceClass, T interfaceInstance) {
        String maybeClassName = interfaceInstance.getClass().getCanonicalName() + "$Proxy";
        int numberOfInstances =
                PythonBytecodeToJavaBytecodeTranslator.classNameToSharedInstanceCount.merge(maybeClassName, 1, Integer::sum);
        if (numberOfInstances > 1) {
            maybeClassName = maybeClassName + "$$" + numberOfInstances;
        }
        String className = maybeClassName;
        String internalClassName = className.replace('.', '/');

        var classWriter = new ClassWriter(ClassWriter.COMPUTE_MAXS | ClassWriter.COMPUTE_FRAMES);

        classWriter.visit(Opcodes.V11, Modifier.PUBLIC, internalClassName, null,
                Type.getInternalName(Object.class), new String[] { Type.getInternalName(interfaceClass) });

        classWriter.visitField(Modifier.PUBLIC | Modifier.STATIC, "proxy",
                Type.getDescriptor(interfaceClass), null, null);

        var constructor = classWriter.visitMethod(Modifier.PUBLIC, "<init>",
                Type.getMethodDescriptor(Type.VOID_TYPE), null, null);

        // Generates Proxy() {}
        constructor.visitCode();
        constructor.visitVarInsn(Opcodes.ALOAD, 0);
        constructor.visitMethodInsn(Opcodes.INVOKESPECIAL, Type.getInternalName(Object.class),
                "<init>", Type.getMethodDescriptor(Type.VOID_TYPE), false);
        constructor.visitInsn(Opcodes.RETURN);
        constructor.visitMaxs(0, 0);
        constructor.visitEnd();

        var interfaceMethod = PythonBytecodeToJavaBytecodeTranslator.getFunctionalInterfaceMethod(interfaceClass);
        var interfaceMethodDescriptor = Type.getMethodDescriptor(interfaceMethod);

        // Generates interfaceMethod(A a, B b, ...) { return proxy.interfaceMethod(a, b, ...); }
        var interfaceMethodVisitor = classWriter.visitMethod(Modifier.PUBLIC, interfaceMethod.getName(),
                interfaceMethodDescriptor, null, null);

        for (var parameter : interfaceMethod.getParameters()) {
            interfaceMethodVisitor.visitParameter(parameter.getName(), 0);
        }
        interfaceMethodVisitor.visitCode();
        interfaceMethodVisitor.visitFieldInsn(Opcodes.GETSTATIC, internalClassName, "proxy",
                Type.getDescriptor(interfaceClass));
        for (int i = 0; i < interfaceMethod.getParameterCount(); i++) {
            interfaceMethodVisitor.visitVarInsn(Type.getType(interfaceMethod.getParameterTypes()[i]).getOpcode(Opcodes.ILOAD),
                    i + 1);
        }
        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEINTERFACE, Type.getInternalName(interfaceClass),
                interfaceMethod.getName(), interfaceMethodDescriptor, true);
        interfaceMethodVisitor.visitInsn(Type.getType(interfaceMethod.getReturnType()).getOpcode(Opcodes.IRETURN));
        interfaceMethodVisitor.visitMaxs(0, 0);
        interfaceMethodVisitor.visitEnd();

        classWriter.visitEnd();

        PythonBytecodeToJavaBytecodeTranslator.writeClassOutput(BuiltinTypes.classNameToBytecode, className,
                classWriter.toByteArray());

        try {
            Class<T> compiledClass = (Class<T>) BuiltinTypes.asmClassLoader.loadClass(className);
            compiledClass.getField("proxy").set(null, interfaceInstance);
            return compiledClass;
        } catch (ClassNotFoundException e) {
            throw new IllegalStateException(("Impossible State: Unable to load generated class (%s)" +
                    " despite it being just generated.").formatted(className), e);
        } catch (NoSuchFieldException | IllegalAccessException e) {
            throw new IllegalStateException(("Impossible State: Unable to access field on generated class (%s).")
                    .formatted(className), e);
        }
    }

    /**
     * Generate an interface that construct a new instance of a type and delegate all calls to that type's methods.
     */
    public static <T> Class<T> generateProxyForClass(Class<T> interfaceClass, PythonLikeType classType) {
        String maybeClassName = classType.getClass().getCanonicalName() + "$" + interfaceClass.getSimpleName() + "$Proxy";
        int numberOfInstances =
                PythonBytecodeToJavaBytecodeTranslator.classNameToSharedInstanceCount.merge(maybeClassName, 1, Integer::sum);
        if (numberOfInstances > 1) {
            maybeClassName = maybeClassName + "$$" + numberOfInstances;
        }
        String className = maybeClassName;
        String internalClassName = className.replace('.', '/');

        var classWriter = new ClassWriter(ClassWriter.COMPUTE_MAXS | ClassWriter.COMPUTE_FRAMES);

        classWriter.visit(Opcodes.V11, Modifier.PUBLIC, internalClassName, null,
                Type.getInternalName(Object.class), new String[] { Type.getInternalName(interfaceClass) });

        classWriter.visitField(Modifier.PRIVATE | Modifier.FINAL, "delegate",
                classType.getJavaTypeDescriptor(), null, null);

        var createdNameSet = new HashSet<String>();
        for (var interfaceMethod : interfaceClass.getMethods()) {
            if (createdNameSet.contains(interfaceMethod.getName()) || !interfaceMethod.getDeclaringClass().isInterface()) {
                continue;
            }
            var methodType = classType.getMethodType(interfaceMethod.getName());
            if (methodType.isEmpty()) {
                if (interfaceMethod.isDefault()) {
                    continue;
                }
                throw new IllegalArgumentException("Type %s cannot implement interface %s because it missing method %s."
                        .formatted(classType, interfaceClass, interfaceMethod));
            }
            var function = methodType.get().getDefaultFunctionSignature();
            if (function.isEmpty()) {
                throw new IllegalStateException();
            }
            classWriter.visitField(Modifier.PUBLIC | Modifier.STATIC, "argumentSpec$" + interfaceMethod.getName(),
                    Type.getDescriptor(ArgumentSpec.class), null, null);
            createdNameSet.add(interfaceMethod.getName());
        }

        var constructor = classWriter.visitMethod(Modifier.PUBLIC, "<init>",
                Type.getMethodDescriptor(Type.VOID_TYPE), null, null);

        // Generates Proxy() {
        //     delegate = new Delegate();
        // }
        constructor.visitCode();
        constructor.visitVarInsn(Opcodes.ALOAD, 0);
        constructor.visitMethodInsn(Opcodes.INVOKESPECIAL, Type.getInternalName(Object.class),
                "<init>", Type.getMethodDescriptor(Type.VOID_TYPE), false);
        constructor.visitVarInsn(Opcodes.ALOAD, 0);
        constructor.visitTypeInsn(Opcodes.NEW, classType.getJavaTypeInternalName());
        constructor.visitInsn(Opcodes.DUP);
        constructor.visitMethodInsn(Opcodes.INVOKESPECIAL, classType.getJavaTypeInternalName(), "<init>",
                Type.getMethodDescriptor(Type.VOID_TYPE), false);
        constructor.visitFieldInsn(Opcodes.PUTFIELD, internalClassName, "delegate", classType.getJavaTypeDescriptor());
        constructor.visitInsn(Opcodes.RETURN);
        constructor.visitMaxs(0, 0);
        constructor.visitEnd();

        for (var interfaceMethod : interfaceClass.getMethods()) {
            if (!interfaceMethod.getDeclaringClass().isInterface()) {
                continue;
            }
            if (interfaceMethod.isDefault()) {
                // Default method, does not need to be present
                var methodType = classType.getMethodType(interfaceMethod.getName());
                if (methodType.isEmpty()) {
                    continue;
                }
                var function = methodType.get().getDefaultFunctionSignature();
                if (function.isEmpty()) {
                    continue;
                }
            }
            var interfaceMethodDescriptor = Type.getMethodDescriptor(interfaceMethod);

            // Generates interfaceMethod(A a, B b, ...) { return delegate.interfaceMethod(a, b, ...); }
            var interfaceMethodVisitor = classWriter.visitMethod(Modifier.PUBLIC, interfaceMethod.getName(),
                    interfaceMethodDescriptor, null, null);

            interfaceMethodVisitor =
                    MethodVisitorAdapters.adapt(interfaceMethodVisitor, interfaceMethod.getName(), interfaceMethodDescriptor);

            for (var parameter : interfaceMethod.getParameters()) {
                interfaceMethodVisitor.visitParameter(parameter.getName(), 0);
            }
            interfaceMethodVisitor.visitCode();
            interfaceMethodVisitor.visitVarInsn(Opcodes.ALOAD, 0);
            interfaceMethodVisitor.visitFieldInsn(Opcodes.GETFIELD, internalClassName, "delegate",
                    classType.getJavaTypeDescriptor());
            interfaceMethodVisitor.visitTypeInsn(Opcodes.NEW, Type.getInternalName(IdentityHashMap.class));
            interfaceMethodVisitor.visitInsn(Opcodes.DUP);
            interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESPECIAL, Type.getInternalName(IdentityHashMap.class),
                    "<init>", Type.getMethodDescriptor(Type.VOID_TYPE), false);
            interfaceMethodVisitor.visitVarInsn(Opcodes.ASTORE, interfaceMethod.getParameterCount() + 1);

            var pythonMethodDescriptor = classType.getMethodType(interfaceMethod.getName())
                    .orElseThrow()
                    .getDefaultFunctionSignature()
                    .orElseThrow()
                    .getMethodDescriptor();
            interfaceMethodVisitor.visitFieldInsn(Opcodes.GETSTATIC, internalClassName,
                    "argumentSpec$" + interfaceMethod.getName(),
                    Type.getDescriptor(ArgumentSpec.class));
            interfaceMethodVisitor.visitLdcInsn(interfaceMethod.getParameterCount());
            interfaceMethodVisitor.visitTypeInsn(Opcodes.ANEWARRAY, Type.getInternalName(PythonLikeObject.class));
            interfaceMethodVisitor.visitVarInsn(Opcodes.ASTORE, interfaceMethod.getParameterCount() + 2);
            for (int i = 0; i < interfaceMethod.getParameterCount(); i++) {
                var parameterType = interfaceMethod.getParameterTypes()[i];
                interfaceMethodVisitor.visitVarInsn(Opcodes.ALOAD, interfaceMethod.getParameterCount() + 2);
                interfaceMethodVisitor.visitLdcInsn(i);
                interfaceMethodVisitor.visitVarInsn(Type.getType(parameterType).getOpcode(Opcodes.ILOAD),
                        i + 1);
                if (parameterType.isPrimitive()) {
                    if (parameterType.equals(boolean.class)) {
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Boolean.class),
                                "valueOf", Type.getMethodDescriptor(Type.getType(Boolean.class), Type.BOOLEAN_TYPE), false);
                    } else if (parameterType.equals(byte.class)) {
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Byte.class),
                                "valueOf", Type.getMethodDescriptor(Type.getType(Byte.class), Type.BYTE_TYPE), false);
                    } else if (parameterType.equals(char.class)) {
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Character.class),
                                "valueOf", Type.getMethodDescriptor(Type.getType(Character.class), Type.CHAR_TYPE), false);
                    } else if (parameterType.equals(short.class)) {
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Short.class),
                                "valueOf", Type.getMethodDescriptor(Type.getType(Short.class), Type.SHORT_TYPE), false);
                    } else if (parameterType.equals(int.class)) {
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Integer.class),
                                "valueOf", Type.getMethodDescriptor(Type.getType(Integer.class), Type.INT_TYPE), false);
                    } else if (parameterType.equals(long.class)) {
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Long.class),
                                "valueOf", Type.getMethodDescriptor(Type.getType(Long.class), Type.LONG_TYPE), false);
                    } else if (parameterType.equals(float.class)) {
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Float.class),
                                "valueOf", Type.getMethodDescriptor(Type.getType(Float.class), Type.FLOAT_TYPE), false);
                    } else if (parameterType.equals(double.class)) {
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Double.class),
                                "valueOf", Type.getMethodDescriptor(Type.getType(Double.class), Type.DOUBLE_TYPE), false);
                    } else {
                        throw new IllegalStateException("Unknown primitive type %s.".formatted(parameterType));
                    }
                }
                interfaceMethodVisitor.visitVarInsn(Opcodes.ALOAD, interfaceMethod.getParameterCount() + 1);
                interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC,
                        Type.getInternalName(JavaPythonTypeConversionImplementor.class),
                        "wrapJavaObject",
                        Type.getMethodDescriptor(Type.getType(PythonLikeObject.class), Type.getType(Object.class), Type.getType(
                                Map.class)),
                        false);
                interfaceMethodVisitor.visitInsn(Opcodes.AASTORE);
            }

            var functionSignature = classType.getMethodType(interfaceMethod.getName())
                    .orElseThrow(() -> new IllegalArgumentException(
                            "Type %s cannot implement interface %s because it missing method %s."
                                    .formatted(classType, interfaceClass, interfaceMethod)))
                    .getDefaultFunctionSignature()
                    .orElseThrow();

            interfaceMethodVisitor.visitVarInsn(Opcodes.ALOAD, interfaceMethod.getParameterCount() + 2);
            interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(List.class),
                    "of", Type.getMethodDescriptor(Type.getType(List.class), Type.getType(Object[].class)),
                    true);
            interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Collections.class),
                    "emptyMap", Type.getMethodDescriptor(Type.getType(Map.class)), false);
            interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(ArgumentSpec.class),
                    "extractArgumentList", Type.getMethodDescriptor(
                            Type.getType(List.class), Type.getType(List.class), Type.getType(Map.class)),
                    false);

            for (int i = 0; i < functionSignature.getParameterTypes().length; i++) {
                interfaceMethodVisitor.visitInsn(Opcodes.DUP);
                interfaceMethodVisitor.visitLdcInsn(i);
                interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEINTERFACE, Type.getInternalName(List.class),
                        "get", Type.getMethodDescriptor(Type.getType(Object.class), Type.INT_TYPE), true);
                interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST,
                        functionSignature.getParameterTypes()[i].getJavaTypeInternalName());
                interfaceMethodVisitor.visitInsn(Opcodes.SWAP);
            }
            interfaceMethodVisitor.visitInsn(Opcodes.POP);
            functionSignature.getMethodDescriptor().callMethod(interfaceMethodVisitor);

            var returnType = interfaceMethod.getReturnType();
            if (returnType.equals(void.class)) {
                interfaceMethodVisitor.visitInsn(Opcodes.RETURN);
            } else {
                if (returnType.isPrimitive()) {
                    if (returnType.equals(boolean.class)) {
                        interfaceMethodVisitor.visitLdcInsn(Type.getType(Boolean.class));
                    } else if (returnType.equals(byte.class)) {
                        interfaceMethodVisitor.visitLdcInsn(Type.getType(Byte.class));
                    } else if (returnType.equals(char.class)) {
                        interfaceMethodVisitor.visitLdcInsn(Type.getType(Character.class));
                    } else if (returnType.equals(short.class)) {
                        interfaceMethodVisitor.visitLdcInsn(Type.getType(Short.class));
                    } else if (returnType.equals(int.class)) {
                        interfaceMethodVisitor.visitLdcInsn(Type.getType(Integer.class));
                    } else if (returnType.equals(long.class)) {
                        interfaceMethodVisitor.visitLdcInsn(Type.getType(Long.class));
                    } else if (returnType.equals(float.class)) {
                        interfaceMethodVisitor.visitLdcInsn(Type.getType(Float.class));
                    } else if (returnType.equals(double.class)) {
                        interfaceMethodVisitor.visitLdcInsn(Type.getType(Double.class));
                    } else {
                        throw new IllegalStateException("Unknown primitive type %s.".formatted(returnType));
                    }
                } else {
                    interfaceMethodVisitor.visitLdcInsn(Type.getType(returnType));
                }
                interfaceMethodVisitor.visitInsn(Opcodes.SWAP);
                interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC,
                        Type.getInternalName(JavaPythonTypeConversionImplementor.class),
                        "convertPythonObjectToJavaType",
                        Type.getMethodDescriptor(Type.getType(Object.class), Type.getType(Class.class), Type.getType(
                                PythonLikeObject.class)),
                        false);
                if (returnType.isPrimitive()) {
                    if (returnType.equals(boolean.class)) {
                        interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Boolean.class));
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Boolean.class),
                                "booleanValue", Type.getMethodDescriptor(Type.BOOLEAN_TYPE), false);
                    } else if (returnType.equals(byte.class)) {
                        interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Byte.class));
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Byte.class),
                                "byteValue", Type.getMethodDescriptor(Type.BYTE_TYPE), false);
                    } else if (returnType.equals(char.class)) {
                        interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Character.class));
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Character.class),
                                "charValue", Type.getMethodDescriptor(Type.CHAR_TYPE), false);
                    } else if (returnType.equals(short.class)) {
                        interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Short.class));
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Short.class),
                                "shortValue", Type.getMethodDescriptor(Type.SHORT_TYPE), false);
                    } else if (returnType.equals(int.class)) {
                        interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Integer.class));
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Integer.class),
                                "intValue", Type.getMethodDescriptor(Type.INT_TYPE), false);
                    } else if (returnType.equals(long.class)) {
                        interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Long.class));
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Long.class),
                                "longValue", Type.getMethodDescriptor(Type.LONG_TYPE), false);
                    } else if (returnType.equals(float.class)) {
                        interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Float.class));
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Float.class),
                                "floatValue", Type.getMethodDescriptor(Type.FLOAT_TYPE), false);
                    } else if (returnType.equals(double.class)) {
                        interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Double.class));
                        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Double.class),
                                "doubleValue", Type.getMethodDescriptor(Type.DOUBLE_TYPE), false);
                    } else {
                        throw new IllegalStateException("Unknown primitive type %s.".formatted(returnType));
                    }
                    interfaceMethodVisitor.visitInsn(Type.getType(returnType).getOpcode(Opcodes.IRETURN));
                } else {
                    interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(returnType));
                    interfaceMethodVisitor.visitInsn(Opcodes.ARETURN);
                }
            }
            interfaceMethodVisitor.visitMaxs(interfaceMethod.getParameterCount() + 2, 1);
            interfaceMethodVisitor.visitEnd();
        }

        classWriter.visitEnd();

        PythonBytecodeToJavaBytecodeTranslator.writeClassOutput(BuiltinTypes.classNameToBytecode, className,
                classWriter.toByteArray());

        try {
            Class<T> compiledClass = (Class<T>) BuiltinTypes.asmClassLoader.loadClass(className);
            for (var interfaceMethod : interfaceClass.getMethods()) {
                if (!interfaceMethod.getDeclaringClass().isInterface()) {
                    continue;
                }
                if (interfaceMethod.isDefault()) {
                    // Default method, does not need to be present
                    var methodType = classType.getMethodType(interfaceMethod.getName());
                    if (methodType.isEmpty()) {
                        continue;
                    }
                    var function = methodType.get().getDefaultFunctionSignature();
                    if (function.isEmpty()) {
                        continue;
                    }
                    compiledClass.getField("argumentSpec$" + interfaceMethod.getName()).set(null,
                            function.get().getArgumentSpec());
                } else {
                    compiledClass.getField("argumentSpec$" + interfaceMethod.getName()).set(null,
                            classType.getMethodType(interfaceMethod.getName())
                                    .orElseThrow()
                                    .getDefaultFunctionSignature()
                                    .orElseThrow()
                                    .getArgumentSpec());
                }
            }
            return compiledClass;
        } catch (ClassNotFoundException | IllegalAccessException | NoSuchFieldException e) {
            throw new IllegalStateException(("Impossible State: Unable to load generated class (%s)" +
                    " despite it being just generated.").formatted(className), e);
        }
    }
}
