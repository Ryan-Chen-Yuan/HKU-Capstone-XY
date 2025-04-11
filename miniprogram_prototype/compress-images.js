const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

// 压缩图片的目录
const imageDir = path.join(__dirname, 'images');

// 确保sharp已安装
console.log('请先运行: npm install sharp');

// 压缩图片函数
async function compressImage(filePath) {
  try {
    const fileName = path.basename(filePath);
    const outputPath = path.join(imageDir, `compressed_${fileName}`);
    
    // 使用sharp压缩图片
    await sharp(filePath)
      .resize(800, 800, { // 调整大小，保持比例
        fit: 'inside',
        withoutEnlargement: true
      })
      .jpeg({ quality: 80 }) // 设置JPEG质量
      .toFile(outputPath);
    
    // 获取原始文件和新文件的大小
    const originalSize = fs.statSync(filePath).size;
    const newSize = fs.statSync(outputPath).size;
    
    console.log(`压缩 ${fileName}: ${(originalSize / 1024).toFixed(2)}KB -> ${(newSize / 1024).toFixed(2)}KB (节省 ${((1 - newSize / originalSize) * 100).toFixed(2)}%)`);
    
    return true;
  } catch (error) {
    console.error(`压缩 ${filePath} 失败:`, error);
    return false;
  }
}

// 主函数
async function main() {
  console.log('开始压缩图片...');
  
  // 获取所有图片文件
  const files = fs.readdirSync(imageDir).filter(file => {
    const ext = path.extname(file).toLowerCase();
    return ['.jpg', '.jpeg', '.png', '.gif'].includes(ext);
  });
  
  console.log(`找到 ${files.length} 个图片文件`);
  
  // 压缩每个图片
  let successCount = 0;
  for (const file of files) {
    const filePath = path.join(imageDir, file);
    const success = await compressImage(filePath);
    if (success) successCount++;
  }
  
  console.log(`压缩完成: ${successCount}/${files.length} 个文件成功压缩`);
}

// 运行主函数
main().catch(console.error); 