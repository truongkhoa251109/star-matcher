import random

# ==========================================
# 1. THIẾT LẬP THÔNG SỐ (PARAMETERS)
# ==========================================
NUM_STARS = 3000
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# Khoảng cách dịch chuyển thực sự
TRUE_SHIFT_X = 15.5
TRUE_SHIFT_Y = -8.2

# Thông số tọa độ & nhiễu
NOISE_RADIUS = 0.5      
DROP_PROB = 0.1         
ADD_NEW_STARS = 255       

# Cường độ sáng
MIN_INTENSITY = 20.0       
MAX_INTENSITY = 250.0      
INTENSITY_NOISE = 15.0   

# ==========================================
# 2. HÀM TẠO FILE TXT
# ==========================================
def save_to_txt(filename, points):
    with open(filename, 'w') as f:
        for x, y, intensity in points:
            # Ghi vào file theo định dạng: x, y, intensity
            f.write(f"{x:.3f}, {y:.3f}, {intensity:.3f}\n")
    print(f"Đã lưu {len(points)} điểm dữ liệu vào {filename}")

# ==========================================
# 3. TẠO DỮ LIỆU FILE 1 (OLD CENTROIDS)
# ==========================================
old_centroids = []
for _ in range(NUM_STARS):
    x = random.uniform(0, IMAGE_WIDTH)
    y = random.uniform(0, IMAGE_HEIGHT)
    # Random độ sáng cho ngôi sao
    intensity = random.uniform(MIN_INTENSITY, MAX_INTENSITY)
    old_centroids.append((x, y, intensity))

save_to_txt("old_centroids.txt", old_centroids)

# ==========================================
# 4. TẠO DỮ LIỆU FILE 2 (NEW CENTROIDS)
# ==========================================
new_centroids = []
for x, y, intensity in old_centroids:
    if random.random() > DROP_PROB:
        new_x = x + TRUE_SHIFT_X + random.uniform(-NOISE_RADIUS, NOISE_RADIUS)
        new_y = y + TRUE_SHIFT_Y + random.uniform(-NOISE_RADIUS, NOISE_RADIUS)
        
        new_intensity = intensity + random.uniform(-INTENSITY_NOISE, INTENSITY_NOISE)
        new_intensity = max(0.0, min(new_intensity, 255.0)) 
        
        new_centroids.append((new_x, new_y, new_intensity))

for _ in range(ADD_NEW_STARS):
    x = random.uniform(0, IMAGE_WIDTH)
    y = random.uniform(0, IMAGE_HEIGHT)
    intensity = random.uniform(MIN_INTENSITY, MAX_INTENSITY)
    new_centroids.append((x, y, intensity))

random.shuffle(new_centroids)
save_to_txt("new_centroids.txt", new_centroids)

print(f"Pixel Jump Xấp xỉ: dx = {TRUE_SHIFT_X}, dy = {TRUE_SHIFT_Y}")
