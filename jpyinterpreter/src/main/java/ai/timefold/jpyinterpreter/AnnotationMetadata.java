package ai.timefold.jpyinterpreter;

import java.lang.annotation.Annotation;
import java.lang.reflect.Array;
import java.util.Map;

import org.objectweb.asm.AnnotationVisitor;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.FieldVisitor;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Type;

public record AnnotationMetadata(Class<? extends Annotation> annotationType, Map<String, Object> annotationValueMap) {
    public void addAnnotationTo(ClassVisitor classVisitor) {
        visitAnnotation(classVisitor.visitAnnotation(Type.getDescriptor(annotationType), true));
    }

    public void addAnnotationTo(FieldVisitor fieldVisitor) {
        visitAnnotation(fieldVisitor.visitAnnotation(Type.getDescriptor(annotationType), true));
    }

    public void addAnnotationTo(MethodVisitor methodVisitor) {
        visitAnnotation(methodVisitor.visitAnnotation(Type.getDescriptor(annotationType), true));
    }

    private void visitAnnotation(AnnotationVisitor annotationVisitor) {
        for (var entry : annotationValueMap.entrySet()) {
            var annotationAttributeName = entry.getKey();
            var annotationAttributeValue = entry.getValue();

            visitAnnotationAttribute(annotationVisitor, annotationAttributeName, annotationAttributeValue);
        }
        annotationVisitor.visitEnd();
    }

    private void visitAnnotationAttribute(AnnotationVisitor annotationVisitor, String attributeName, Object attributeValue) {
        if (attributeValue instanceof Number
                || attributeValue instanceof Boolean
                || attributeValue instanceof Character
                || attributeValue instanceof String) {
            annotationVisitor.visit(attributeName, attributeValue);
            return;
        }

        if (attributeValue instanceof Class<?> clazz) {
            annotationVisitor.visit(attributeName, Type.getType(clazz));
            return;
        }

        if (attributeValue instanceof AnnotationMetadata annotationMetadata) {
            annotationMetadata.visitAnnotation(
                    annotationVisitor.visitAnnotation(attributeName, Type.getDescriptor(annotationMetadata.annotationType)));
            return;
        }

        if (attributeValue instanceof Enum<?> enumValue) {
            annotationVisitor.visitEnum(attributeName, Type.getDescriptor(enumValue.getClass()),
                    enumValue.name());
            return;
        }

        if (attributeValue.getClass().isArray()) {
            var arrayAnnotationVisitor = annotationVisitor.visitArray(attributeName);
            var arrayLength = Array.getLength(attributeValue);
            for (int i = 0; i < arrayLength; i++) {
                visitAnnotationAttribute(arrayAnnotationVisitor, attributeName, Array.get(attributeValue, i));
            }
            arrayAnnotationVisitor.visitEnd();
            return;
        }
        throw new IllegalArgumentException("Annotation of type %s has an illegal value %s for attribute %s."
                .formatted(annotationType, attributeValue, attributeName));
    }
}
