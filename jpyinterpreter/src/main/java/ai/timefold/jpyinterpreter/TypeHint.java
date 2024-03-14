package ai.timefold.jpyinterpreter;

import java.util.List;

import ai.timefold.jpyinterpreter.types.PythonLikeType;

public record TypeHint(PythonLikeType type, List<AnnotationMetadata> annotationList) {
    public static TypeHint withoutAnnotations(PythonLikeType type) {
        return new TypeHint(type, List.of());
    }

}
