package ai.timefold.jpyinterpreter;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import ai.timefold.jpyinterpreter.types.PythonLikeType;

public record TypeHint(PythonLikeType type, List<AnnotationMetadata> annotationList, TypeHint[] genericArgs) {
    public TypeHint {
        annotationList = Collections.unmodifiableList(annotationList);
    }

    public TypeHint(PythonLikeType type, List<AnnotationMetadata> annotationList) {
        this(type, annotationList, null);
    }

    public TypeHint addAnnotations(List<AnnotationMetadata> addedAnnotations) {
        List<AnnotationMetadata> combinedAnnotations = new ArrayList<>(annotationList.size() + addedAnnotations.size());
        combinedAnnotations.addAll(annotationList);
        combinedAnnotations.addAll(addedAnnotations);
        return new TypeHint(type, combinedAnnotations, genericArgs);
    }

    public static TypeHint withoutAnnotations(PythonLikeType type) {
        return new TypeHint(type, Collections.emptyList());
    }

}
