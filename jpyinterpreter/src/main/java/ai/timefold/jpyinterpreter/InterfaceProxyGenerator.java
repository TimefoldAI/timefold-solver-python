package ai.timefold.jpyinterpreter;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Collections;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import ai.timefold.jpyinterpreter.implementors.JavaPythonTypeConversionImplementor;
import ai.timefold.jpyinterpreter.types.BuiltinTypes;
import ai.timefold.jpyinterpreter.types.PythonLikeType;
import ai.timefold.jpyinterpreter.util.MethodVisitorAdapters;
import ai.timefold.jpyinterpreter.util.arguments.ArgumentSpec;

import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.MethodVisitor;
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
    public static <T> Class<T> generateProxyForClass(Class<T> interfaceClass, PythonLikeType delegateType) {
        String maybeClassName = delegateType.getClass().getCanonicalName() + "$" + interfaceClass.getSimpleName() + "$Proxy";
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
                delegateType.getJavaTypeDescriptor(), null, null);

        var createdNameSet = new HashSet<String>();
        for (var interfaceMethod : interfaceClass.getMethods()) {
            addArgumentSpecFieldForMethod(classWriter, delegateType, interfaceMethod, createdNameSet);
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
        constructor.visitTypeInsn(Opcodes.NEW, delegateType.getJavaTypeInternalName());
        constructor.visitInsn(Opcodes.DUP);
        constructor.visitMethodInsn(Opcodes.INVOKESPECIAL, delegateType.getJavaTypeInternalName(), "<init>",
                Type.getMethodDescriptor(Type.VOID_TYPE), false);
        constructor.visitFieldInsn(Opcodes.PUTFIELD, internalClassName, "delegate", delegateType.getJavaTypeDescriptor());
        constructor.visitInsn(Opcodes.RETURN);
        constructor.visitMaxs(0, 0);
        constructor.visitEnd();

        for (var interfaceMethod : interfaceClass.getMethods()) {
            createMethodDelegate(classWriter, internalClassName, delegateType, interfaceMethod);
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
                    var methodType = delegateType.getMethodType(interfaceMethod.getName());
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
                            delegateType.getMethodType(interfaceMethod.getName())
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

    private static void addArgumentSpecFieldForMethod(ClassWriter classWriter,
            PythonLikeType delegateType, Method interfaceMethod, Set<String> createdNameSet) {
        if (createdNameSet.contains(interfaceMethod.getName()) || !interfaceMethod.getDeclaringClass().isInterface()) {
            return;
        }
        var methodType = delegateType.getMethodType(interfaceMethod.getName());
        if (methodType.isEmpty()) {
            if (interfaceMethod.isDefault()) {
                return;
            }
            throw new IllegalArgumentException("Type %s cannot implement interface %s because it missing method %s."
                    .formatted(delegateType, interfaceMethod.getDeclaringClass(), interfaceMethod));
        }
        var function = methodType.get().getDefaultFunctionSignature();
        if (function.isEmpty()) {
            throw new IllegalStateException();
        }
        classWriter.visitField(Modifier.PUBLIC | Modifier.STATIC, "argumentSpec$" + interfaceMethod.getName(),
                Type.getDescriptor(ArgumentSpec.class), null, null);
        createdNameSet.add(interfaceMethod.getName());
    }

    private static void createMethodDelegate(ClassWriter classWriter,
            String wrapperInternalName,
            PythonLikeType delegateType, Method interfaceMethod) {
        if (!interfaceMethod.getDeclaringClass().isInterface()) {
            return;
        }
        if (interfaceMethod.isDefault()) {
            // Default method, does not need to be present
            var methodType = delegateType.getMethodType(interfaceMethod.getName());
            if (methodType.isEmpty()) {
                return;
            }
            var function = methodType.get().getDefaultFunctionSignature();
            if (function.isEmpty()) {
                return;
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
        interfaceMethodVisitor.visitFieldInsn(Opcodes.GETFIELD, wrapperInternalName, "delegate",
                delegateType.getJavaTypeDescriptor());
        interfaceMethodVisitor.visitTypeInsn(Opcodes.NEW, Type.getInternalName(IdentityHashMap.class));
        interfaceMethodVisitor.visitInsn(Opcodes.DUP);
        interfaceMethodVisitor.visitMethodInsn(Opcodes.INVOKESPECIAL, Type.getInternalName(IdentityHashMap.class),
                "<init>", Type.getMethodDescriptor(Type.VOID_TYPE), false);
        interfaceMethodVisitor.visitVarInsn(Opcodes.ASTORE, interfaceMethod.getParameterCount() + 1);

        interfaceMethodVisitor.visitFieldInsn(Opcodes.GETSTATIC, wrapperInternalName,
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
                convertPrimitiveToObjectType(parameterType, interfaceMethodVisitor);
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

        var functionSignature = delegateType.getMethodType(interfaceMethod.getName())
                .orElseThrow(() -> new IllegalArgumentException(
                        "Type %s cannot implement interface %s because it missing method %s."
                                .formatted(delegateType, interfaceMethod.getDeclaringClass(), interfaceMethod)))
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
                loadBoxedPrimitiveTypeClass(returnType, interfaceMethodVisitor);
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
                unboxBoxedPrimitiveType(returnType, interfaceMethodVisitor);
                interfaceMethodVisitor.visitInsn(Type.getType(returnType).getOpcode(Opcodes.IRETURN));
            } else {
                interfaceMethodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(returnType));
                interfaceMethodVisitor.visitInsn(Opcodes.ARETURN);
            }
        }
        interfaceMethodVisitor.visitMaxs(interfaceMethod.getParameterCount() + 2, 1);
        interfaceMethodVisitor.visitEnd();
    }

    private static void convertPrimitiveToObjectType(Class<?> primitiveType, MethodVisitor methodVisitor) {
        if (primitiveType.equals(boolean.class)) {
            methodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Boolean.class),
                    "valueOf", Type.getMethodDescriptor(Type.getType(Boolean.class), Type.BOOLEAN_TYPE), false);
        } else if (primitiveType.equals(byte.class)) {
            methodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Byte.class),
                    "valueOf", Type.getMethodDescriptor(Type.getType(Byte.class), Type.BYTE_TYPE), false);
        } else if (primitiveType.equals(char.class)) {
            methodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Character.class),
                    "valueOf", Type.getMethodDescriptor(Type.getType(Character.class), Type.CHAR_TYPE), false);
        } else if (primitiveType.equals(short.class)) {
            methodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Short.class),
                    "valueOf", Type.getMethodDescriptor(Type.getType(Short.class), Type.SHORT_TYPE), false);
        } else if (primitiveType.equals(int.class)) {
            methodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Integer.class),
                    "valueOf", Type.getMethodDescriptor(Type.getType(Integer.class), Type.INT_TYPE), false);
        } else if (primitiveType.equals(long.class)) {
            methodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Long.class),
                    "valueOf", Type.getMethodDescriptor(Type.getType(Long.class), Type.LONG_TYPE), false);
        } else if (primitiveType.equals(float.class)) {
            methodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Float.class),
                    "valueOf", Type.getMethodDescriptor(Type.getType(Float.class), Type.FLOAT_TYPE), false);
        } else if (primitiveType.equals(double.class)) {
            methodVisitor.visitMethodInsn(Opcodes.INVOKESTATIC, Type.getInternalName(Double.class),
                    "valueOf", Type.getMethodDescriptor(Type.getType(Double.class), Type.DOUBLE_TYPE), false);
        } else {
            throw new IllegalStateException("Unknown primitive type %s.".formatted(primitiveType));
        }
    }

    private static void loadBoxedPrimitiveTypeClass(Class<?> primitiveType, MethodVisitor methodVisitor) {
        if (primitiveType.equals(boolean.class)) {
            methodVisitor.visitLdcInsn(Type.getType(Boolean.class));
        } else if (primitiveType.equals(byte.class)) {
            methodVisitor.visitLdcInsn(Type.getType(Byte.class));
        } else if (primitiveType.equals(char.class)) {
            methodVisitor.visitLdcInsn(Type.getType(Character.class));
        } else if (primitiveType.equals(short.class)) {
            methodVisitor.visitLdcInsn(Type.getType(Short.class));
        } else if (primitiveType.equals(int.class)) {
            methodVisitor.visitLdcInsn(Type.getType(Integer.class));
        } else if (primitiveType.equals(long.class)) {
            methodVisitor.visitLdcInsn(Type.getType(Long.class));
        } else if (primitiveType.equals(float.class)) {
            methodVisitor.visitLdcInsn(Type.getType(Float.class));
        } else if (primitiveType.equals(double.class)) {
            methodVisitor.visitLdcInsn(Type.getType(Double.class));
        } else {
            throw new IllegalStateException("Unknown primitive type %s.".formatted(primitiveType));
        }
    }

    private static void unboxBoxedPrimitiveType(Class<?> primitiveType, MethodVisitor methodVisitor) {
        if (primitiveType.equals(boolean.class)) {
            methodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Boolean.class));
            methodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Boolean.class),
                    "booleanValue", Type.getMethodDescriptor(Type.BOOLEAN_TYPE), false);
        } else if (primitiveType.equals(byte.class)) {
            methodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Byte.class));
            methodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Byte.class),
                    "byteValue", Type.getMethodDescriptor(Type.BYTE_TYPE), false);
        } else if (primitiveType.equals(char.class)) {
            methodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Character.class));
            methodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Character.class),
                    "charValue", Type.getMethodDescriptor(Type.CHAR_TYPE), false);
        } else if (primitiveType.equals(short.class)) {
            methodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Short.class));
            methodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Short.class),
                    "shortValue", Type.getMethodDescriptor(Type.SHORT_TYPE), false);
        } else if (primitiveType.equals(int.class)) {
            methodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Integer.class));
            methodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Integer.class),
                    "intValue", Type.getMethodDescriptor(Type.INT_TYPE), false);
        } else if (primitiveType.equals(long.class)) {
            methodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Long.class));
            methodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Long.class),
                    "longValue", Type.getMethodDescriptor(Type.LONG_TYPE), false);
        } else if (primitiveType.equals(float.class)) {
            methodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Float.class));
            methodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Float.class),
                    "floatValue", Type.getMethodDescriptor(Type.FLOAT_TYPE), false);
        } else if (primitiveType.equals(double.class)) {
            methodVisitor.visitTypeInsn(Opcodes.CHECKCAST, Type.getInternalName(Double.class));
            methodVisitor.visitMethodInsn(Opcodes.INVOKEVIRTUAL, Type.getInternalName(Double.class),
                    "doubleValue", Type.getMethodDescriptor(Type.DOUBLE_TYPE), false);
        } else {
            throw new IllegalStateException("Unknown primitive type %s.".formatted(primitiveType));
        }
    }
}
