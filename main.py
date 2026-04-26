import numpy as np
from pathlib import Path
from collections import defaultdict

class GridCentroidMatcher:
    def __init__(self, dist_threshold=50.0, intensity_tolerance=30.0, min_match_ratio=0.1):
        self.dist_threshold = dist_threshold
        self.intensity_tolerance = intensity_tolerance
        self.min_match_ratio = min_match_ratio
        self.grid_size = dist_threshold 

    def load_centroids(self, filepath):
        file_path = Path(filepath)
        
        try:
            data = np.loadtxt(file_path, delimiter=',')
            if data.ndim == 1:
                data = data.reshape(1, -1)
            return data
        except Exception as e:
            raise ValueError(f"Lỗi định dạng file {filepath}: {e}")

    def _get_grid_key(self, x, y):
        return int(x // self.grid_size), int(y // self.grid_size)

    def _build_spatial_grid(self, data):
        grid = defaultdict(list)
        for i in range(len(data)):
            x, y, intensity = data[i]
            key = self._get_grid_key(x, y)
            grid[key].append({
                'coords': np.array([x, y]),
                'intensity': intensity
            })
        return grid

    def match_frames(self, old_frame_path, new_frame_path):
        old_data = self.load_centroids(old_frame_path)
        new_data = self.load_centroids(new_frame_path)


        new_grid = self._build_spatial_grid(new_data)
        
        matched_old = []
        matched_new = []

        for x_old, y_old, intensity_old in old_data:
            cell_x, cell_y = self._get_grid_key(x_old, y_old)
            
            best_candidate = None
            min_intensity_diff = self.intensity_tolerance

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    neighbor_key = (cell_x + dx, cell_y + dy)
                    
                    if neighbor_key not in new_grid:
                        continue
                    
                    for candidate in new_grid[neighbor_key]:
                        dist = np.linalg.norm(np.array([x_old, y_old]) - candidate['coords'])
                        
                        if dist <= self.dist_threshold:
                            intensity_diff = abs(intensity_old - candidate['intensity'])
                            
                            if intensity_diff < min_intensity_diff:
                                min_intensity_diff = intensity_diff
                                best_candidate = candidate['coords']

            if best_candidate is not None:
                matched_old.append([x_old, y_old])
                matched_new.append(best_candidate)

        matched_old = np.array(matched_old)
        matched_new = np.array(matched_new)
        
        required_matches = max(5, int(len(old_data) * self.min_match_ratio))
        if len(matched_old) < required_matches:
            raise RuntimeError(f"Tỷ lệ khớp quá thấp: {len(matched_old)} sao.")

        shifts = matched_new - matched_old
        median_shift = np.median(shifts, axis=0)
        deviations = np.linalg.norm(shifts - median_shift, axis=1)
        inliers = shifts[deviations < 2.0]

        final_jump = np.mean(inliers, axis=0)

        return final_jump[0], final_jump[1], len(inliers)

if __name__ == "__main__":
    matcher = GridCentroidMatcher(dist_threshold=40.0, intensity_tolerance=25.0)
    
    dx, dy, total_stars = matcher.match_frames("old_centroids.txt", "new_centroids.txt")
    
    print("-" * 30)
    print(f"(dx): {dx:+.3f} px")
    print(f"(dy): {dy:+.3f} px")
    print(f"Mactching star: {total_stars}")
    print("-" * 30)