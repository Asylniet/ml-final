export interface PredictionResponse {
  prediction: string;
  is_mirna: boolean;
  confidence: number;
  gc_content: number;
  length: number;
  sequence: string;
}
