import os
import pickle

import numpy
from pipeline_01_config_setup_fun import read_params
import pandas as pd
import argparse
import numpy as np
import time
from datetime import datetime

class ModelInference:
    """
    A comprehensive class for performing model inference, including loading the model, preprocessing input data, and generating predictions.
    """

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None

    def load_model(self):
        """
        Load the trained model from the specified path.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at: {self.model_path}")

        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)

        return self.model
    
    def model_inference(self, input_data):
        """
        Perform inference using the loaded model on the provided input data.
        """
        if self.model is None:
            raise ValueError("Model is not loaded. Please load the model before performing inference.")

        # Here you would include any necessary preprocessing steps for the input_data
        # For example, if your model expects a specific format, you would transform input_data accordingly

        predictions = self.model.predict(input_data)
        return predictions


def main(data_init=False):
    """
    Main function to perform model inference.
    """
    input_data = None  # Replace with actual input data for inference
    config = read_params(os.path.join("config", "params.yaml"))
    model_path = config["saved_models"]["model_dir"]
    inference = ModelInference(model_path + "/best_model.pkl")
    model = inference.load_model()
    print("Model loaded successfully:", type(model))

    if data_init:
        # Initialize input_data with dummy data for testing purposes
        input_data = pd.DataFrame([[-0.1355199558643293,-1.3974104675213597,-0.0436636951368608,0.4962305571742278,0.1901422094611682,0.0344104039648007,0.6564202108157732,0.4110763859335697,0.5697668111091828,-0.1205176348942463,-0.1268390912515736,2.033487676053904,-0.6456089814151296,-1.7682951425913402,-0.05187288745891,-0.0358360893252537,-0.2202470920509122,0.3170877837899783,0.3385491955249182,2.6613961833338395,1.5145001106248855e-16,-0.0892606604731885,-0.0158822800665333,0.3100774306463221,-0.2297974549854701,0.1923145128256107,-0.3307407574314417,-0.2266652381262637,0.6417098373049347,-0.0314177396168879,-1.1485445717473473,-0.2513318627163896,-0.5637900930104123,0.2365433704046494,-0.1954856245733606,0.1747984367759543,-7.039347660977129e-16,-0.0509234675052388,0.5313336573410947,-0.4119465291500894,-0.3060906692044917,-0.8513741983087512,2.931766649410934,0.0,-1.1093000717285182,-0.0254575692209623,-0.8448490721380661,1.1891067028901108,0.1959283143918466,-0.115419713262912,-0.9188416579914352,-0.0240553034907226,-3.371044220675002e-15,-0.8060787816829231,-0.2771197385149884,0.6995686940763757,-0.0356154479842456,-0.5087965232639861,0.4194327961009655,0.5375705950805532]])
        print("Dummy input data initialized for inference:", input_data)
    predictions = inference.model_inference(input_data)  # Replace input_data with actual data for inference
    print("Predictions:", predictions)

    predictions_saved = {
        "Inference_Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "Input_data": input_data.iloc[0].tolist(),
        "Prediction": predictions.tolist()
    }
    print(predictions_saved)

    if not os.path.exists("data/Prediction_Output_File"):
        os.makedirs("data/Prediction_Output_File")
    saved_path = os.path.join("data/Prediction_Output_File", "Predictions.csv")
    pd.DataFrame([predictions_saved]).to_csv(saved_path,
                                     index=False,
                                     mode='a' if os.path.exists(saved_path) else 'w',
                                     header=["Inference_Time", "Input_data", "Prediction"] if not os.path.exists(saved_path) else False)


    print("Model inference completed.")
    return inference


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "--dummy_data",
        action="store_true",
        help="Use dummy input data for inference",
    )
    args = args.parse_args()
    inference = main(data_init=args.dummy_data)