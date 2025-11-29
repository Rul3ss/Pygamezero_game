from PIL import Image
import os

# Espelha as imagens do bunny de 1 a 8
for i in range(1, 9):  # 1 até 8
    img = Image. open(f'bunny_{i}.png')
    img_flipped = img.transpose(Image. FLIP_LEFT_RIGHT)
    img_flipped.save(f'bunny_left_{i}.png')
    print(f'✅ Criado: bunny_left_{i}.png')

print(f'\n🎉 Total: 8 imagens espelhadas criadas!')
