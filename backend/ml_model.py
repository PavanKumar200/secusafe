"""
ml_model.py — Upgraded phishing detector with 20+ features,
VotingClassifier ensemble, SMOTE oversampling, and retrain() function.
"""
import os
import joblib
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

logger = logging.getLogger(__name__)

# ── Feature names (order matters — must match scraper output) ──────────────
FEATURE_NAMES = [
    # Original 13
    "url_length", "has_ip", "subdomain_count", "suspicious_tld",
    "form_count", "input_count", "external_links", "hidden_elements",
    "urgency_keywords", "countdown_timers", "fake_notifications",
    "has_https", "popup_count",
    # New 7 numeric features
    "url_entropy",
    "domain_age_days",
    "redirect_count",
    "domain_changed_on_redirect",
    "has_mx_record",
    "typosquat_score",
    "js_obfuscation_count",
    # ssl features use fixed indices too
    "ssl_days_remaining",
    "ssl_self_signed",
    # DNS
    "has_spf_record",
    "has_dmarc_record",
]


class PhishingDetector:
    """Ensemble phishing classifier supporting training, prediction, and retraining."""

    def __init__(self):
        self.feature_names = FEATURE_NAMES
        self.model = self._build_ensemble()

    # ── Model construction ────────────────────────────────────────────────

    def _build_ensemble(self):
        """Build the VotingClassifier ensemble."""
        rf = RandomForestClassifier(
            n_estimators=200, class_weight="balanced", random_state=42, n_jobs=-1
        )
        xgb = GradientBoostingClassifier(n_estimators=150, random_state=42)
        lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
        return VotingClassifier(
            estimators=[("rf", rf), ("xgb", xgb), ("lr", lr)],
            voting="soft",
        )

    # ── Core ML methods ───────────────────────────────────────────────────

    def train(self, X, y):
        """Train the ensemble model with labeled data."""
        self.model.fit(X, y)

    def retrain(self, csv_path: str = None):
        """
        Retrain from a CSV file with SMOTE oversampling.
        CSV must contain all feature columns + a 'label' column (0=benign, 1=phishing).
        Saves the new model to models/trained_model.pkl.
        """
        import pandas as pd
        from imblearn.over_sampling import SMOTE
        from config import MODEL_PATH, TRAINING_DATA_FILE

        if csv_path is None:
            csv_path = TRAINING_DATA_FILE

        print(f"[ML] Loading training data from {csv_path} ...")
        df = pd.read_csv(csv_path)

        # Ensure all feature columns exist; fill missing with 0
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0

        X = df[self.feature_names].fillna(0).values
        y = df["label"].values

        print(f"[ML] Original dataset: {len(y)} samples, {int(y.sum())} phishing")

        # SMOTE oversampling
        sm = SMOTE(random_state=42)
        X_res, y_res = sm.fit_resample(X, y)
        print(f"[ML] After SMOTE: {len(y_res)} samples")

        # Rebuild and train fresh ensemble
        self.model = self._build_ensemble()
        self.model.fit(X_res, y_res)

        # Print report (use a small validation split)
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(
            X_res, y_res, test_size=0.2, random_state=42
        )
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_val)
        print("[ML] Classification Report:")
        print(classification_report(y_val, y_pred, target_names=["Benign", "Phishing"]))

        # Save model
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        self.save_model(MODEL_PATH)
        print(f"[ML] Model saved to {MODEL_PATH}")

    def predict(self, features: dict) -> float:
        """
        Predict phishing probability from a feature dict.

        Returns:
            float: probability (0.0 – 1.0) of being malicious
        """
        feature_array = np.array(
            [[self._safe_get(features, name) for name in self.feature_names]]
        )
        probability = self.model.predict_proba(feature_array)[0][1]
        return float(probability)

    def get_feature_importance(self, features: dict) -> list:
        """
        Return top-5 feature importances as sorted list of dicts.

        Returns:
            list of {"feature": str, "importance": float, "value": float}
        """
        try:
            # VotingClassifier: average importances from RF and GBM estimators
            importances = np.zeros(len(self.feature_names))
            count = 0
            for name, est in self.model.named_estimators_.items():
                if hasattr(est, "feature_importances_"):
                    importances += est.feature_importances_
                    count += 1
            if count > 0:
                importances /= count

            feature_scores = []
            for i, name in enumerate(self.feature_names):
                val = self._safe_get(features, name)
                feature_scores.append(
                    {
                        "feature": name,
                        "value": float(val),
                        "importance": round(float(importances[i]), 4),
                    }
                )
            feature_scores.sort(key=lambda x: x["importance"], reverse=True)
            return feature_scores[:5]
        except Exception as e:
            logger.warning(f"Feature importance failed: {e}")
            return []

    # ── Persistence ───────────────────────────────────────────────────────

    def save_model(self, filepath: str):
        """Serialize model to disk using joblib."""
        joblib.dump(self.model, filepath)

    def load_model(self, filepath: str):
        """Deserialize model from disk using joblib."""
        self.model = joblib.load(filepath)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _safe_get(self, features: dict, name: str) -> float:
        """Get feature value; return 0 if missing or string (e.g. closest_brand)."""
        val = features.get(name, 0)
        if isinstance(val, str):
            return 0.0
        try:
            fval = float(val)
            # Treat -1 (lookup failure) as 0 for ML
            return 0.0 if fval < 0 else fval
        except (TypeError, ValueError):
            return 0.0