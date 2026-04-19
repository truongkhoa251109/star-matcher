import numpy as np
from scipy.spatial import KDTree
from pathlib import Path

class CentroidMatcher:
    def __init__(self, dist_threshold=50.0, intensity_tolerance=30.0, min_match_ratio=0.1):
        self.dist_threshold = dist_threshold
        self.intensity_tolerance = intensity_tolerance
        self.min_match_ratio = min_match_ratio

    def load_centroids(self, filepath):
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileNotFoundError(f"Missing file {filepath}")
        
        data = np.loadtxt(file_path, delimiter=',')
        if data.ndim == 1:
            data = data.reshape(1, -1)
        return data

    def match_frames(self, old_frame_path, new_frame_path):
        old_data = self.load_centroids(old_frame_path)
        new_data = self.load_centroids(new_frame_path)

        if len(old_data) < 5 or len(new_data) < 5:
            raise ValueError("Insufficient stars for tracking.")

        old_coords, old_intensity = old_data[:, :2], old_data[:, 2]
        new_coords, new_intensity = new_data[:, :2], new_data[:, 2]

        tree = KDTree(new_coords)
        distances, indices = tree.query(old_coords, k=3, distance_upper_bound=self.dist_threshold)

        matched_old = []
        matched_new = []

        for i, old_star_coord in enumerate(old_coords):
            best_candidate_idx = -1
            min_intensity_diff = self.intensity_tolerance
            
            for neighbor_idx in indices[i]:
                if neighbor_idx >= len(new_coords):
                    continue
                
                intensity_diff = abs(old_intensity[i] - new_intensity[neighbor_idx])
                
                if intensity_diff < min_intensity_diff:
                    min_intensity_diff = intensity_diff
                    best_candidate_idx = neighbor_idx
            
            if best_candidate_idx != -1:
                matched_old.append(old_star_coord)
                matched_new.append(new_coords[best_candidate_idx])

        matched_old = np.array(matched_old)
        matched_new = np.array(matched_new)

        required_matches = max(5, int(len(old_data) * self.min_match_ratio))
        if len(matched_old) < required_matches:
            raise RuntimeError(f"Match ratio too low ({len(matched_old)} matches).")

        shifts = matched_new - matched_old
        median_shift = np.median(shifts, axis=0)
        
        deviations = np.linalg.norm(shifts - median_shift, axis=1)
        inliers = shifts[deviations < 2.0]

        if len(inliers) < 3:
            raise RuntimeError("Motion inconsistency detected.")

        final_jump = np.mean(inliers, axis=0)

        return final_jump[0], final_jump[1], len(inliers)

if __name__ == "__main__":
    matcher = CentroidMatcher()
    
    try:
        dx, dy, valid_matches = matcher.match_frames("old_centroids.txt", "new_centroids.txt")
        print(f"Success -> dx: {dx:.3f}, dy: {dy:.3f} | Inliers: {valid_matches}")
    except Exception as error:
        print(error)