"""
SignBridge Fast & Rigorous Machine Learning Training & Evaluation Pipeline (v3.0)
Trains Random Forest, SVM (RBF), and MLP classifiers with Stratified Cross Validation.
Generates academic evaluation metrics and presentation-ready figures:
- Confusion Matrix Heatmap (32 classes)
- PCA 2D Sign Clusters Plot
- Random Forest Feature Importance Ranking (Top 15 out of 89 features)
- Model Performance Comparison Chart
"""

import os
import json
import joblib
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.model_selection import StratifiedKFold, train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score
from sklearn.decomposition import PCA

from .synthetic_data import generate_augmented_dataset, SIGNS_LIST

def train_and_evaluate(dataset_path: str = "SignBridge/data/dataset.npz", output_dir: str = "SignBridge/models", results_dir: str = "SignBridge/results"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(results_dir).mkdir(parents=True, exist_ok=True)

    # 1. Load or Generate Dataset
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Generating augmented dataset...")
        X, y, classes = generate_augmented_dataset(samples_per_class=120, output_path=dataset_path)
    else:
        print(f"Loading dataset from {dataset_path}...")
        data = np.load(dataset_path, allow_pickle=True)
        X = data['X']
        y = data['y']
        classes = list(data['classes'])

    print(f"Loaded {len(X)} samples across {len(classes)} classes with {X.shape[1]} features.")

    # 2. Train / Test Split (80% train, 20% test stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )

    # 3. Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save Scaler and Class mapping
    joblib.dump(scaler, os.path.join(output_dir, "scaler.joblib"))
    with open(os.path.join(output_dir, "classes.json"), "w") as f:
        json.dump(classes, f, indent=2)

    # 4. Models Configuration (Optimized for speed and high precision)
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=16, random_state=42, n_jobs=-1),
        "SVM (RBF Kernel)": SVC(C=5.0, kernel='rbf', gamma='scale', probability=True, random_state=42),
        "MLP Classifier": MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=250, random_state=42)
    }

    results = {}
    fitted_models = {}

    print("\n--- Model Training & Cross-Validation (Stratified K-Fold) ---")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for name, model in models.items():
        t0 = time.time()
        print(f"Evaluating {name}...")
        
        # Fast CV scoring (using non-probabilistic fast mode for SVM CV)
        if name == "SVM (RBF Kernel)":
            fast_svm = SVC(C=5.0, kernel='rbf', gamma='scale', random_state=42)
            cv_scores = cross_val_score(fast_svm, X_train_scaled, y_train, cv=3, scoring='accuracy', n_jobs=-1)
        else:
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='accuracy', n_jobs=-1)
        
        # Fit final model on full training set
        model.fit(X_train_scaled, y_train)
        fit_time = time.time() - t0
        
        # Inference latency benchmark
        t_lat0 = time.time()
        for _ in range(50):
            _ = model.predict(X_test_scaled[:1])
        latency_ms = ((time.time() - t_lat0) / 50.0) * 1000.0

        y_pred = model.predict(X_test_scaled)
        test_acc = accuracy_score(y_test, y_pred)
        test_f1 = f1_score(y_test, y_pred, average='macro')

        results[name] = {
            "cv_acc_mean": float(np.mean(cv_scores)),
            "cv_acc_std": float(np.std(cv_scores)),
            "test_acc": float(test_acc),
            "test_f1": float(test_f1),
            "latency_ms": float(latency_ms),
            "y_pred": y_pred
        }
        fitted_models[name] = model
        print(f"  -> CV Accuracy: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores):.4f}) | Fit time: {fit_time:.1f}s")
        print(f"  -> Test Accuracy: {test_acc:.4f} | Macro-F1: {test_f1:.4f} | CPU Latency: {latency_ms:.2f} ms")

    # Save models
    joblib.dump(fitted_models["Random Forest"], os.path.join(output_dir, "rf_model.joblib"))
    joblib.dump(fitted_models["SVM (RBF Kernel)"], os.path.join(output_dir, "svm_model.joblib"))
    print("\nModels successfully saved to", output_dir)

    # 5. Generate Visual Artifacts for Presentation

    # A. Model Comparison Bar Chart
    plt.figure(figsize=(9, 5), dpi=300)
    model_names = list(results.keys())
    accs = [results[m]["test_acc"] for m in model_names]
    f1s = [results[m]["test_f1"] for m in model_names]

    x = np.arange(len(model_names))
    width = 0.35
    plt.bar(x - width/2, accs, width, label='Test Accuracy', color='#2563eb')
    plt.bar(x + width/2, f1s, width, label='Macro-F1 Score', color='#10b981')
    plt.xticks(x, model_names, fontweight='bold', fontsize=11)
    plt.ylim(0.0, 1.05)
    plt.ylabel('Score (0.0 - 1.0)', fontweight='bold', fontsize=11)
    plt.title('SignBridge 32-Class Model Performance Comparison', fontsize=13, fontweight='bold', pad=15)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(loc='lower right', fontsize=10)
    for i in range(len(model_names)):
        plt.text(x[i] - width/2, accs[i] + 0.02, f"{accs[i]*100:.1f}%", ha='center', fontweight='bold', fontsize=9.5)
        plt.text(x[i] + width/2, f1s[i] + 0.02, f"{f1s[i]*100:.1f}%", ha='center', fontweight='bold', fontsize=9.5)
    plt.tight_layout()
    comparison_path = os.path.join(results_dir, "model_comparison.png")
    plt.savefig(comparison_path, dpi=300)
    plt.close()
    print(f"Saved: {comparison_path}")

    # B. Confusion Matrix for Best Model
    best_model_name = "Random Forest" if results["Random Forest"]["test_acc"] >= results["SVM (RBF Kernel)"]["test_acc"] else "SVM (RBF Kernel)"
    best_pred = results[best_model_name]["y_pred"]
    cm = confusion_matrix(y_test, best_pred)
    plt.figure(figsize=(15, 13), dpi=300)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes, cbar=False)
    plt.title(f'SignBridge {best_model_name} Confusion Matrix (32 Classes)', fontsize=15, fontweight='bold', pad=15)
    plt.xlabel('Predicted Sign', fontsize=12, fontweight='bold')
    plt.ylabel('Ground Truth Sign', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=9.5)
    plt.yticks(rotation=0, fontsize=9.5)
    plt.tight_layout()
    cm_path = os.path.join(results_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"Saved: {cm_path}")

    # C. Random Forest Feature Importance (Top 15 features)
    rf_model = fitted_models["Random Forest"]
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1][:15]

    feature_labels = [
        f"Feat #{i}: " + (
            "Inter-wrist Distance" if i == 74 else
            "Wrist Vert Offset" if i == 75 else
            "Fist-Palm Contact" if i == 78 else
            "Palm Normal Align" if i == 79 else
            "Index Tip Z (Depth)" if i == 35 or i == 72 else
            "Palm Normal Y (Facing)" if i == 30 or i == 67 else
            "Thumb-Index Pinch" if i == 33 or i == 70 else
            "Hand Presence" if i in [74, 75] else
            f"Joint Angle #{i%15}" if i < 30 else
            f"Extension Ratio #{i%5}"
        ) for i in indices[::-1]
    ]

    plt.figure(figsize=(11, 6), dpi=300)
    plt.title('Top 15 Most Discriminative Geometric Features (Random Forest)', fontsize=13, fontweight='bold', pad=15)
    plt.barh(range(15), importances[indices][::-1], color='#8b5cf6', align='center')
    plt.yticks(range(15), feature_labels, fontweight='bold', fontsize=9.5)
    plt.xlabel('Relative Feature Importance (Gini Purity Gain)', fontsize=11, fontweight='bold')
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    feat_path = os.path.join(results_dir, "feature_importance.png")
    plt.savefig(feat_path, dpi=300)
    plt.close()
    print(f"Saved: {feat_path}")

    # D. PCA 2D Clustering of Signs
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_test_scaled)
    plt.figure(figsize=(12, 8), dpi=300)
    selected_signs = ["I", "YOU", "WHERE", "HELP", "HOSPITAL", "FEVER", "PAIN", "TODAY"]
    selected_indices = [classes.index(s) for s in selected_signs if s in classes]
    palette = sns.color_palette("bright", len(selected_indices))
    
    for i, class_idx in enumerate(selected_indices):
        mask = (y_test == class_idx)
        plt.scatter(X_pca[mask, 0], X_pca[mask, 1], label=classes[class_idx], color=palette[i], alpha=0.85, s=50)

    plt.title('SignBridge Feature Space Clusters (PCA 2D Projection)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(f'Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% Variance)', fontsize=11, fontweight='bold')
    plt.ylabel(f'Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% Variance)', fontsize=11, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., fontsize=10.5)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    pca_path = os.path.join(results_dir, "pca_clusters.png")
    plt.savefig(pca_path, dpi=300)
    plt.close()
    print(f"Saved: {pca_path}")

    # Save summary metrics
    summary = {
        "num_classes": len(classes),
        "num_features": X.shape[1],
        "total_samples": len(X),
        "results": {
            k: {m: v for m, v in val.items() if m != "y_pred"} for k, val in results.items()
        }
    }
    with open(os.path.join(results_dir, "metrics_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("Training and evaluation completed successfully!")
    return results

if __name__ == "__main__":
    train_and_evaluate()
