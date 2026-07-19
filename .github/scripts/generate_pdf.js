const puppeteer = require('puppeteer');
const path = require('path');

const inputFile = process.argv[2];
const outputFile = process.argv[3];

if (!inputFile || !outputFile) {
  console.error("Usage: node generate_pdf.js <input.html> <output.pdf>");
  process.exit(1);
}

(async () => {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  const inputUrl = `file://${path.resolve(inputFile)}`;
  
  await page.goto(inputUrl, { waitUntil: 'networkidle0' });
  await page.pdf({
    path: outputFile,
    format: 'A4',
    printBackground: true,
    margin: { top: '1cm', bottom: '1cm', left: '1cm', right: '1cm' },
    landscape: true // diffは横幅を取るのでランドスケープの方が見やすいことが多い
  });
  
  await browser.close();
})();
