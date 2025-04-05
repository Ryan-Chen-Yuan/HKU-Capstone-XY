const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

// 确保sharp已安装
console.log('请先运行: npm install sharp');

// 创建简单的图标
async function createIcon(name, color) {
  const size = 48;
  const svg = `
    <svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
      <rect width="${size}" height="${size}" fill="white" />
      <text x="50%" y="50%" font-family="Arial" font-size="24" fill="${color}" text-anchor="middle" dominant-baseline="middle">${name}</text>
    </svg>
  `;
  
  const outputPath = path.join(__dirname, 'images', `${name}.png`);
  
  await sharp(Buffer.from(svg))
    .png()
    .toFile(outputPath);
  
  console.log(`创建图标: ${outputPath}`);
}

// 主函数
async function main() {
  // 创建首页图标
  await createIcon('home', '#999999');
  await createIcon('home-active', '#07C160');
  
  // 创建发现图标
  await createIcon('discover', '#999999');
  await createIcon('discover-active', '#07C160');
  
  // 创建我的图标
  await createIcon('profile', '#999999');
  await createIcon('profile-active', '#07C160');
  
  console.log('所有图标创建完成');
}

// 运行主函数
main().catch(console.error); 