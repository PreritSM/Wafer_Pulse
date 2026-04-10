from datetime import datetime
import logging
import os
import pickle

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split
import xgboost as xgb

from src.infrastructure.mlflow_tracking import configure_mlflow, log_run_metadata
from src.pipeline_01_config_setup_fun import read_params

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    A comprehensive model training class with hyperparameter tuning.
    Designed to be modular for MLflow integration.
    """

    def __init__(self, config):
        self.config = config
        self.models = {}
        self.best_params = {}
        self.training_results = {}

    def load_data(self):
        """Load the selected features dataset for training."""
        print("Loading training data...")
        data_path = os.path.join(
            self.config["data_source"]["Train_Data_dir"], "selected_features_secom_data.csv"
        )

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Training data not found at: {data_path}")

        df = pd.read_csv(data_path)
        print(f"Data loaded successfully. Shape: {df.shape}")

        # Separate features and target
        X = df.drop(self.config["base"]["target_col"], axis=1)
        y = df[self.config["base"]["target_col"]]

        print(f"Features shape: {X.shape}")
        print(f"Target distribution:\n{y.value_counts()}")

        return X, y

    def split_data(self, X, y):
        """Split data into train and test sets."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.config["base"]["random_state"], stratify=y
        )

        print(f"Training set shape: {X_train.shape}")
        print(f"Test set shape: {X_test.shape}")

        return X_train, X_test, y_train, y_test

    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """Train Random Forest with hyperparameter tuning."""
        print("\n" + "=" * 60)
        print("Training Random Forest Classifier")
        print("=" * 60)

        # Get Random Forest parameters from config
        rf_params = self.config["training"]["random_forest"]

        # Initialize the model
        rf = RandomForestClassifier(random_state=self.config["base"]["random_state"], n_jobs=-1)

        # Setup GridSearchCV
        grid_search = GridSearchCV(
            estimator=rf,
            param_grid=rf_params["param_grid"],
            cv=rf_params["cv"],
            scoring="accuracy",
            verbose=rf_params["verbose"],
            n_jobs=-1,
        )

        # Train the model
        print("Starting hyperparameter tuning...")
        grid_search.fit(X_train, y_train)

        # Store results
        self.models["random_forest"] = grid_search.best_estimator_
        self.best_params["random_forest"] = grid_search.best_params_

        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best cross-validation score: {grid_search.best_score_:.4f}")

        # Evaluate on test set
        test_predictions = grid_search.best_estimator_.predict(X_test)
        test_proba = grid_search.best_estimator_.predict_proba(X_test)[:, 1]

        # Calculate metrics
        metrics = self._calculate_metrics(y_test, test_predictions, test_proba)
        self.training_results["random_forest"] = {
            "best_params": grid_search.best_params_,
            "cv_score": grid_search.best_score_,
            "test_metrics": metrics,
        }

        print("\nRandom Forest Test Set Results:")
        self._print_metrics(metrics)

        return grid_search.best_estimator_

    def train_xgboost(self, X_train, y_train, X_test, y_test):
        """Train XGBoost with hyperparameter tuning."""
        print("\n" + "=" * 60)
        print("Training XGBoost Classifier")
        print("=" * 60)

        # Get XGBoost parameters from config
        xgb_params = self.config["training"]["xg_boost"]

        # Initialize the model
        xgb_clf = xgb.XGBClassifier(
            random_state=self.config["base"]["random_state"], eval_metric="logloss", n_jobs=-1
        )

        # Setup GridSearchCV
        grid_search = GridSearchCV(
            estimator=xgb_clf,
            param_grid=xgb_params["param_grid"],
            cv=xgb_params["cv"],
            scoring="accuracy",
            verbose=xgb_params["verbose"],
            n_jobs=-1,
        )

        # Train the model
        print("Starting hyperparameter tuning...")
        grid_search.fit(X_train, y_train)

        # Store results
        self.models["xgboost"] = grid_search.best_estimator_
        self.best_params["xgboost"] = grid_search.best_params_

        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best cross-validation score: {grid_search.best_score_:.4f}")

        # Evaluate on test set
        test_predictions = grid_search.best_estimator_.predict(X_test)
        test_proba = grid_search.best_estimator_.predict_proba(X_test)[:, 1]

        # Calculate metrics
        metrics = self._calculate_metrics(y_test, test_predictions, test_proba)
        self.training_results["xgboost"] = {
            "best_params": grid_search.best_params_,
            "cv_score": grid_search.best_score_,
            "test_metrics": metrics,
        }

        print("\nXGBoost Test Set Results:")
        self._print_metrics(metrics)

        return grid_search.best_estimator_

    def _calculate_metrics(self, y_true, y_pred, y_proba):
        """Calculate comprehensive evaluation metrics."""
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average="weighted"),
            "recall": recall_score(y_true, y_pred, average="weighted"),
            "f1_score": f1_score(y_true, y_pred, average="weighted"),
            "roc_auc": roc_auc_score(y_true, y_proba),
            "pr_auc": average_precision_score(y_true, y_proba),
        }
        return metrics

    def _print_metrics(self, metrics):
        """Print metrics in a formatted way."""
        for metric, value in metrics.items():
            print(f"{metric.upper()}: {value:.4f}")

    def compare_models(self):
        """Compare all trained models and select the best one."""
        print("\n" + "=" * 60)
        print("Model Comparison Summary")
        print("=" * 60)

        best_model = None
        best_score = 0
        best_model_name = ""

        for model_name, results in self.training_results.items():
            print(f"\n{model_name.upper()}:")
            print(f"  CV Score: {results['cv_score']:.4f}")
            print(f"  Test Accuracy: {results['test_metrics']['accuracy']:.4f}")
            print(f"  Test F1: {results['test_metrics']['f1_score']:.4f}")
            print(f"  Test PR AUC: {results['test_metrics']['pr_auc']:.4f}")
            print(f"  Test ROC AUC: {results['test_metrics']['roc_auc']:.4f}")

            # PR-AUC is the primary selection metric for imbalanced data.
            if results["test_metrics"]["pr_auc"] > best_score:
                best_score = results["test_metrics"]["pr_auc"]
                best_model = self.models[model_name]
                best_model_name = model_name

        print(f"\n🏆 Best Model: {best_model_name.upper()} (PR-AUC: {best_score:.4f})")
        return best_model, best_model_name

    def save_models(self):
        """Save all trained models and results."""
        print("\nSaving models and results...")

        # Create models directory
        models_dir = self.config["saved_models"]["model_dir"]
        os.makedirs(models_dir, exist_ok=True)

        # Save each model
        for model_name, model in self.models.items():
            model_path = os.path.join(models_dir, f"{model_name}_model.pkl")
            joblib.dump(model, model_path)
            print(f"Saved {model_name} to: {model_path}")

        # Save best parameters
        params_path = os.path.join(models_dir, "best_params.pkl")
        with open(params_path, "wb") as f:
            pickle.dump(self.best_params, f)
        print(f"Saved best parameters to: {params_path}")

        # Save Best Model separately
        best_model_name = max(
            self.training_results, key=lambda k: self.training_results[k]["test_metrics"]["pr_auc"]
        )
        best_model = self.models[best_model_name]
        best_model_path = os.path.join(models_dir, "best_model.pkl")
        joblib.dump(best_model, best_model_path)
        print(f"Saved best model ({best_model_name}) to: {best_model_path}")

        # Save training results
        results_path = os.path.join(models_dir, "training_results.pkl")
        with open(results_path, "wb") as f:
            pickle.dump(self.training_results, f)
        print(f"Saved training results to: {results_path}")

        # Save detailed report
        report_path = os.path.join(
            self.config["artifacts_dir"]["general"], "model_training_report.txt"
        )
        self._save_detailed_report(report_path)
        print(f"Detailed report saved to: {report_path}")

    def _save_detailed_report(self, report_path):
        """Save a detailed training report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(report_path, "w") as f:
            f.write("Model Training Report\n")
            f.write(f"Generated on: {timestamp}\n")
            f.write("=" * 80 + "\n\n")

            for model_name, results in self.training_results.items():
                f.write(f"{model_name.upper()} RESULTS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Best Parameters: {results['best_params']}\n")
                f.write(f"Cross-Validation Score: {results['cv_score']:.4f}\n")
                f.write("Test Set Metrics:\n")
                for metric, value in results["test_metrics"].items():
                    f.write(f"  {metric}: {value:.4f}\n")
                f.write("\n")

        print(f"Detailed report saved to: {report_path}")


def main():
    """Main training pipeline function."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    logger.info("Starting model training pipeline")

    # Load configuration
    config = read_params(os.path.join("config", "params.yaml"))

    # Initialize trainer
    trainer = ModelTrainer(config)

    try:
        configure_mlflow()
        with mlflow.start_run(run_name="wafer-training"):
            # Load and split data
            X, y = trainer.load_data()
            X_train, X_test, y_train, y_test = trainer.split_data(X, y)

            # Train models
            trainer.train_random_forest(X_train, y_train, X_test, y_test)
            trainer.train_xgboost(X_train, y_train, X_test, y_test)

            # Compare models and select best
            best_model, best_model_name = trainer.compare_models()

            # Save models and results
            trainer.save_models()

            best_metrics = trainer.training_results[best_model_name]["test_metrics"]
            best_params = trainer.training_results[best_model_name]["best_params"]
            log_run_metadata(
                best_model_name=best_model_name, best_params=best_params, metrics=best_metrics
            )
            mlflow.sklearn.log_model(best_model, artifact_path="model")

        print("\n✅ Training completed successfully!")
        print(f"Best performing model: {best_model_name}")

        return trainer

    except Exception as e:
        print(f"❌ Error during training: {str(e)}")
        raise


if __name__ == "__main__":
    trainer = main()
