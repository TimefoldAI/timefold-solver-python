package org.optaplanner.python.translator.types;

import static org.optaplanner.python.translator.types.BuiltinTypes.BASE_TYPE;
import static org.optaplanner.python.translator.types.BuiltinTypes.CLASS_FUNCTION_TYPE;
import static org.optaplanner.python.translator.types.BuiltinTypes.FUNCTION_TYPE;
import static org.optaplanner.python.translator.types.BuiltinTypes.STATIC_FUNCTION_TYPE;
import static org.optaplanner.python.translator.types.BuiltinTypes.TYPE_TYPE;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Stream;

import org.objectweb.asm.Type;
import org.optaplanner.python.translator.FieldDescriptor;
import org.optaplanner.python.translator.PythonBinaryOperators;
import org.optaplanner.python.translator.PythonClassTranslator;
import org.optaplanner.python.translator.PythonFunctionSignature;
import org.optaplanner.python.translator.PythonGenericFunctionSignature;
import org.optaplanner.python.translator.PythonLikeObject;
import org.optaplanner.python.translator.PythonOverloadImplementor;
import org.optaplanner.python.translator.PythonTernaryOperators;
import org.optaplanner.python.translator.PythonUnaryOperator;
import org.optaplanner.python.translator.builtins.TernaryDunderBuiltin;
import org.optaplanner.python.translator.types.collections.PythonLikeDict;
import org.optaplanner.python.translator.types.collections.PythonLikeTuple;
import org.optaplanner.python.translator.types.errors.AttributeError;
import org.optaplanner.python.translator.types.errors.ValueError;

public class PythonLikeType implements PythonLikeObject,
        PythonLikeFunction {
    public final Map<String, PythonLikeObject> __dir__;

    private final String TYPE_NAME;

    private final String JAVA_TYPE_INTERNAL_NAME;
    private final List<PythonLikeType> PARENT_TYPES;

    private final Map<String, PythonKnownFunctionType> functionNameToKnownFunctionType;
    private Optional<PythonKnownFunctionType> constructorKnownFunctionType;

    private final Map<String, FieldDescriptor> instanceFieldToFieldDescriptorMap;

    private PythonLikeFunction constructor;

    public PythonLikeType(String typeName, Class<? extends PythonLikeObject> javaClass) {
        this(typeName, javaClass, List.of(BASE_TYPE));
    }

    public PythonLikeType(String typeName, Class<? extends PythonLikeObject> javaClass, List<PythonLikeType> parents) {
        TYPE_NAME = typeName;
        JAVA_TYPE_INTERNAL_NAME = Type.getInternalName(javaClass);
        PARENT_TYPES = parents;
        constructor = (positional, keywords) -> {
            throw new UnsupportedOperationException("Cannot create instance of type (" + TYPE_NAME + ").");
        };
        __dir__ = new HashMap<>();
        functionNameToKnownFunctionType = new HashMap<>();
        constructorKnownFunctionType = Optional.empty();
        instanceFieldToFieldDescriptorMap = new HashMap<>();
    }

    public PythonLikeType(String typeName, String javaTypeInternalName, List<PythonLikeType> parents) {
        TYPE_NAME = typeName;
        JAVA_TYPE_INTERNAL_NAME = javaTypeInternalName;
        PARENT_TYPES = parents;
        constructor = (positional, keywords) -> {
            throw new UnsupportedOperationException("Cannot create instance of type (" + TYPE_NAME + ").");
        };
        __dir__ = new HashMap<>();
        functionNameToKnownFunctionType = new HashMap<>();
        constructorKnownFunctionType = Optional.empty();
        instanceFieldToFieldDescriptorMap = new HashMap<>();
    }

    public PythonLikeType(String typeName, Class<? extends PythonLikeObject> javaClass, Consumer<PythonLikeType> initializer) {
        this(typeName, javaClass, List.of(BASE_TYPE));
        initializer.accept(this);
    }

    public boolean isInstance(PythonLikeObject object) {
        PythonLikeType objectType = object.__getType();
        return objectType.isSubclassOf(this);
    }

    public static PythonLikeType registerBaseType() {
        try {
            BASE_TYPE.addBinaryMethod(PythonBinaryOperators.GET_ATTRIBUTE,
                    PythonLikeObject.class.getMethod("$method$__getattribute__", PythonString.class));
            BASE_TYPE.addTernaryMethod(PythonTernaryOperators.SET_ATTRIBUTE,
                    PythonLikeObject.class.getMethod("$method$__setattr__", PythonString.class, PythonLikeObject.class));
            BASE_TYPE.addBinaryMethod(PythonBinaryOperators.DELETE_ATTRIBUTE,
                    PythonLikeObject.class.getMethod("$method$__delattr__", PythonString.class));
            BASE_TYPE.addBinaryMethod(PythonBinaryOperators.EQUAL,
                    PythonLikeObject.class.getMethod("$method$__eq__", PythonLikeObject.class));
            BASE_TYPE.addBinaryMethod(PythonBinaryOperators.NOT_EQUAL,
                    PythonLikeObject.class.getMethod("$method$__ne__", PythonLikeObject.class));
            BASE_TYPE.addUnaryMethod(PythonUnaryOperator.AS_STRING, PythonLikeObject.class.getMethod("$method$__str__"));
            BASE_TYPE.addUnaryMethod(PythonUnaryOperator.REPRESENTATION, PythonLikeObject.class.getMethod("$method$__repr__"));
            BASE_TYPE.addUnaryMethod(PythonUnaryOperator.HASH, PythonLikeObject.class.getMethod("$method$__hash__"));
            BASE_TYPE.addBinaryMethod(PythonBinaryOperators.FORMAT,
                    PythonLikeObject.class.getMethod("$method$__format__", PythonLikeObject.class));
            BASE_TYPE.setConstructor((vargs, kwargs) -> new AbstractPythonLikeObject(BASE_TYPE) {
            });

            PythonOverloadImplementor.createDispatchesFor(BASE_TYPE);
        } catch (NoSuchMethodException e) {
            throw new IllegalStateException(e);
        }
        return BASE_TYPE;
    }

    public static PythonLikeType registerTypeType() {
        TYPE_TYPE.setConstructor((positional, keywords) -> {
            if (positional.size() == 1) {
                return positional.get(0).__getType();
            } else if (positional.size() == 3) {
                PythonString name = (PythonString) positional.get(0);
                PythonLikeTuple baseClasses = (PythonLikeTuple) positional.get(1);
                PythonLikeDict dict = (PythonLikeDict) positional.get(2);

                PythonLikeType out;
                if (baseClasses.isEmpty()) {
                    out = new PythonLikeType(name.value, PythonLikeObject.class);
                } else {
                    out = new PythonLikeType(name.value, PythonLikeObject.class, (List) baseClasses);
                }

                for (Map.Entry<PythonLikeObject, PythonLikeObject> entry : dict.entrySet()) {
                    PythonString attributeName = (PythonString) entry.getKey();

                    out.__setAttribute(attributeName.value, entry.getValue());
                }

                return out;
            } else {
                throw new ValueError("type takes 1 or 3 positional arguments, got " + positional.size());
            }
        });

        return TYPE_TYPE;
    }

    @Override
    public PythonLikeObject $method$__getattribute__(PythonString pythonName) {
        String name = pythonName.value;
        PythonLikeObject typeResult = __getAttributeOrNull(name);
        if (typeResult != null) {
            PythonLikeObject maybeDescriptor = typeResult.__getAttributeOrNull(PythonTernaryOperators.GET.dunderMethod);
            if (maybeDescriptor == null) {
                maybeDescriptor = typeResult.__getType().__getAttributeOrNull(PythonTernaryOperators.GET.dunderMethod);
            }

            if (maybeDescriptor != null) {
                if (!(maybeDescriptor instanceof PythonLikeFunction)) {
                    throw new UnsupportedOperationException("'" + maybeDescriptor.__getType() + "' is not callable");
                }
                return TernaryDunderBuiltin.GET_DESCRIPTOR.invoke(typeResult, PythonNone.INSTANCE, this);
            }
            return typeResult;
        }

        throw new AttributeError("object '" + this + "' does not have attribute '" + name + "'");
    }

    public void addMethod(String methodName, Method method) {
        addMethod(methodName, PythonFunctionSignature.forMethod(method));
    }

    public void addUnaryMethod(PythonUnaryOperator operator, Method method) {
        addMethod(operator.getDunderMethod(), PythonFunctionSignature.forMethod(method));
    }

    public void addBinaryMethod(PythonBinaryOperators operator, Method method) {
        addMethod(operator.getDunderMethod(), PythonFunctionSignature.forMethod(method));
        if (operator.hasRightDunderMethod() && !operator.isComparisonMethod()) {
            addMethod(operator.getRightDunderMethod(), PythonFunctionSignature.forMethod(method));
        }
    }

    public void addLeftBinaryMethod(PythonBinaryOperators operator, Method method) {
        addMethod(operator.getDunderMethod(), PythonFunctionSignature.forMethod(method));
    }

    public void addRightBinaryMethod(PythonBinaryOperators operator, Method method) {
        addMethod(operator.getRightDunderMethod(), PythonFunctionSignature.forMethod(method));
    }

    public void addTernaryMethod(PythonTernaryOperators operator, Method method) {
        addMethod(operator.getDunderMethod(), PythonFunctionSignature.forMethod(method));
    }

    public void addUnaryMethod(PythonUnaryOperator operator, PythonFunctionSignature method) {
        addMethod(operator.getDunderMethod(), method);
    }

    public void addBinaryMethod(PythonBinaryOperators operator, PythonFunctionSignature method) {
        addMethod(operator.getDunderMethod(), method);
        if (operator.hasRightDunderMethod() && !operator.isComparisonMethod()) {
            addMethod(operator.getRightDunderMethod(), method);
        }
    }

    public void addLeftBinaryMethod(PythonBinaryOperators operator, PythonFunctionSignature method) {
        addMethod(operator.getDunderMethod(), method);
    }

    public void addRightBinaryMethod(PythonBinaryOperators operator, PythonFunctionSignature method) {
        addMethod(operator.getRightDunderMethod(), method);
    }

    public void addTernaryMethod(PythonTernaryOperators operator, PythonFunctionSignature method) {
        addMethod(operator.getDunderMethod(), method);
    }

    public void addGenericMethod(String methodName, Method method) {
        addMethod(methodName, PythonGenericFunctionSignature.forGenericMethod(method));
    }

    public void addGenericUnaryMethod(PythonUnaryOperator operator, Method method) {
        addMethod(operator.getDunderMethod(), PythonGenericFunctionSignature.forGenericMethod(method));
    }

    public void addGenericBinaryMethod(PythonBinaryOperators operator, Method method) {
        addMethod(operator.getDunderMethod(), method);
        if (operator.hasRightDunderMethod() && !operator.isComparisonMethod()) {
            addMethod(operator.getRightDunderMethod(), method);
        }
    }

    public void addGenericLeftBinaryMethod(PythonBinaryOperators operator, Method method) {
        addMethod(operator.getDunderMethod(), method);
    }

    public void addGenericRightBinaryMethod(PythonBinaryOperators operator, Method method) {
        addMethod(operator.getRightDunderMethod(), method);
    }

    public void addGenericTernaryMethod(PythonTernaryOperators operator, Method method) {
        addMethod(operator.getDunderMethod(), PythonGenericFunctionSignature.forGenericMethod(method));
    }

    public void addMethod(String methodName, PythonFunctionSignature method) {
        PythonKnownFunctionType knownFunctionType = functionNameToKnownFunctionType.computeIfAbsent(methodName,
                key -> new PythonKnownFunctionType(methodName, new ArrayList<>()));
        knownFunctionType.getOverloadFunctionSignatureList().add(method);
    }

    public Set<String> getKnownMethodsDefinedByClass() {
        return functionNameToKnownFunctionType.keySet();
    }

    public Set<String> getKnownMethods() {
        Set<String> out = new HashSet<>();
        getAssignableTypesStream().forEach(type -> out.addAll(type.getKnownMethodsDefinedByClass()));
        return out;
    }

    public void setConstructor(PythonLikeFunction constructor) {
        this.constructor = constructor;
    }

    public void addConstructor(PythonFunctionSignature constructor) {
        if (constructorKnownFunctionType.isEmpty()) {
            constructorKnownFunctionType = Optional.of(new PythonKnownFunctionType("<init>", new ArrayList<>()));
        }
        constructorKnownFunctionType.get().getOverloadFunctionSignatureList().add(constructor);
    }

    public Optional<PythonKnownFunctionType> getMethodType(String methodName) {
        PythonKnownFunctionType out = new PythonKnownFunctionType(methodName, new ArrayList<>());
        getAssignableTypesStream().forEach(type -> {
            PythonKnownFunctionType knownFunctionType = type.functionNameToKnownFunctionType.get(methodName);
            if (knownFunctionType != null) {
                out.getOverloadFunctionSignatureList().addAll(knownFunctionType.getOverloadFunctionSignatureList());
            }
        });

        if (out.getOverloadFunctionSignatureList().isEmpty()) {
            return Optional.empty();
        }

        return Optional.of(out);
    }

    public Optional<PythonClassTranslator.PythonMethodKind> getMethodKind(String methodName) {
        PythonLikeObject maybeMethod = __getAttributeOrNull(methodName);
        if (maybeMethod != null) {
            PythonLikeType methodKind = maybeMethod.__getType();
            if (methodKind == FUNCTION_TYPE) {
                return Optional.of(PythonClassTranslator.PythonMethodKind.VIRTUAL_METHOD);
            }
            if (methodKind == STATIC_FUNCTION_TYPE) {
                return Optional.of(PythonClassTranslator.PythonMethodKind.STATIC_METHOD);
            }
            if (methodKind == CLASS_FUNCTION_TYPE) {
                return Optional.of(PythonClassTranslator.PythonMethodKind.CLASS_METHOD);
            }
            return Optional.empty();
        } else {
            return Optional.empty();
        }
    }

    public Optional<PythonKnownFunctionType> getConstructorType() {
        return constructorKnownFunctionType;
    }

    public Optional<FieldDescriptor> getInstanceFieldDescriptor(String fieldName) {
        return getAssignableTypesStream().map(PythonLikeType::getInstanceFieldToFieldDescriptorMap)
                .filter(map -> map.containsKey(fieldName))
                .map(map -> map.get(fieldName))
                .findAny();
    }

    public void addInstanceField(FieldDescriptor fieldDescriptor) {
        Optional<FieldDescriptor> maybeExistingField = getInstanceFieldDescriptor(fieldDescriptor.getPythonFieldName());
        if (maybeExistingField.isPresent()) {
            PythonLikeType existingFieldType = maybeExistingField.get().getFieldPythonLikeType();
            if (!fieldDescriptor.getFieldPythonLikeType().isSubclassOf(existingFieldType)) {
                throw new IllegalStateException("Field (" + fieldDescriptor.getPythonFieldName() + ") already exist with type ("
                        +
                        existingFieldType + ") which is not assignable from (" + fieldDescriptor.getFieldPythonLikeType()
                        + ").");
            }
        } else {
            instanceFieldToFieldDescriptorMap.put(fieldDescriptor.getPythonFieldName(), fieldDescriptor);
        }
    }

    private Map<String, FieldDescriptor> getInstanceFieldToFieldDescriptorMap() {
        return instanceFieldToFieldDescriptorMap;
    }

    public PythonLikeType unifyWith(PythonLikeType other) {
        Optional<PythonLikeType> maybeCommonType = other.getAssignableTypesStream().filter(otherType -> {
            if (otherType.isSubclassOf(this)) {
                return true;
            }
            return this.isSubclassOf(otherType);
        }).findAny();

        if (maybeCommonType.isPresent() && maybeCommonType.get() != BASE_TYPE) {
            PythonLikeType commonType = maybeCommonType.get();
            if (commonType.isSubclassOf(this)) {
                return this;
            } else {
                return commonType;
            }
        }

        for (PythonLikeType parent : getParentList()) {
            PythonLikeType parentUnification = parent.unifyWith(other);
            if (parentUnification != BASE_TYPE) {
                return parentUnification;
            }
        }
        return BASE_TYPE;
    }

    public boolean isSubclassOf(PythonLikeType type) {
        return isSubclassOf(type, new HashSet<>());
    }

    private Stream<PythonLikeType> getAssignableTypesStream() {
        return Stream.concat(
                Stream.of(this),
                getParentList().stream()
                        .flatMap(PythonLikeType::getAssignableTypesStream))
                .distinct();
    }

    private boolean isSubclassOf(PythonLikeType type, Set<PythonLikeType> visited) {
        if (visited.contains(this)) {
            return false;
        }

        if (this == type) {
            return true;
        }

        visited.add(this);
        for (PythonLikeType parent : PARENT_TYPES) {
            if (parent.isSubclassOf(type, visited)) {
                return true;
            }
        }
        return false;
    }

    public int getDepth() {
        if (PARENT_TYPES.size() == 0) {
            return 0;
        } else {
            return 1 + PARENT_TYPES.stream().map(PythonLikeType::getDepth).max(Comparator.naturalOrder()).get();
        }
    }

    @Override
    public PythonLikeObject __call__(List<PythonLikeObject> positionalArguments,
            Map<PythonString, PythonLikeObject> namedArguments) {
        return constructor.__call__(positionalArguments, namedArguments);
    }

    public PythonLikeObject loadMethod(String methodName) {
        PythonLikeObject out = __getAttributeOrNull(methodName);
        if (out == null) {
            return null;
        }

        if (out.__getType() == PythonLikeFunction.getFunctionType()) {
            return out;
        }

        return null;
        //if (out.__getType() == PythonLikeFunction.getClassFunctionType()) {
        //    return FunctionBuiltinOperations.bindFunctionToType((PythonLikeFunction) out, null, this);
        //} else {
        //    return null;
        //}
    }

    public PythonLikeType getDefiningTypeOrNull(String attributeName) {
        if (__dir__.containsKey(attributeName) &&
                (this == BASE_TYPE
                        || (__dir__.get(attributeName).getClass() != BASE_TYPE.__dir__.get(attributeName).getClass()))) {
            return this;
        }

        for (PythonLikeType parent : PARENT_TYPES) {
            PythonLikeType out = parent.getDefiningTypeOrNull(attributeName);
            if (out != null) {
                return out;
            }
        }
        return null;
    }

    public PythonLikeObject __getAttributeOrNull(String attributeName) {
        PythonLikeObject out = __dir__.get(attributeName);
        if (out == null) {
            for (PythonLikeType type : PARENT_TYPES) {
                out = type.__getAttributeOrNull(attributeName);
                if (out != null) {
                    return out;
                }
            }
            return null;
        } else {
            return out;
        }
    }

    @Override
    public void __setAttribute(String attributeName, PythonLikeObject value) {
        __dir__.put(attributeName, value);
    }

    @Override
    public void __deleteAttribute(String attributeName) {
        // TODO: Descriptors: https://docs.python.org/3/howto/descriptor.html
        __dir__.remove(attributeName);
    }

    @Override
    public PythonLikeType __getType() {
        return new PythonLikeGenericType(this);
    }

    public String getTypeName() {
        return TYPE_NAME;
    }

    public String getJavaTypeInternalName() {
        return JAVA_TYPE_INTERNAL_NAME;
    }

    public String getJavaTypeDescriptor() {
        return "L" + JAVA_TYPE_INTERNAL_NAME + ";";
    }

    /**
     * Return the Java class corresponding to this type, if it exists. Throws {@link ClassNotFoundException} otherwise.
     */
    public Class<?> getJavaClass() throws ClassNotFoundException {
        return Class.forName(JAVA_TYPE_INTERNAL_NAME.replace('/', '.'), true,
                BuiltinTypes.asmClassLoader);
    }

    public List<PythonLikeType> getParentList() {
        return PARENT_TYPES;
    }

    @Override
    public String toString() {
        return "<class " + TYPE_NAME + ">";
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || !PythonLikeType.class.isAssignableFrom(o.getClass())) {
            return false;
        }
        PythonLikeType that = (PythonLikeType) o;
        return JAVA_TYPE_INTERNAL_NAME.equals(that.JAVA_TYPE_INTERNAL_NAME);
    }

    @Override
    public int hashCode() {
        return Objects.hash(JAVA_TYPE_INTERNAL_NAME);
    }
}
