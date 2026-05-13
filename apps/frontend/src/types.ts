export interface PredictionResponse {
  prediction: string;
  is_mirna: boolean;
  confidence: number;
  gc_content: number;
  length: number;
  sequence: string;
<<<<<<< HEAD
  feature_values: Record<string, number>;
  secondary_structure: SecondaryStructure | null;
}

export interface FeatureImportance {
  name: string;
  importance: number;
}

export interface ModelStats {
  accuracy: number;
  f1: number;
  precision: number;
  recall: number;
  cv_score: number;
  n_samples: number;
  n_positive: number;
  n_negative: number;
  n_features: number;
  model_type: string;
}

export interface SecondaryStructure {
  dot_bracket: string;
  mfe: number;
  svg: string;
=======
>>>>>>> d7a84cde81472fa331c529ee30cf2e30082145da
}
