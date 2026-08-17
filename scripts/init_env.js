const fs = require('fs');
const path = require('path');

const envExample = path.join(__dirname, '..', '.env.example');
const envFile = path.join(__dirname, '..', '.env');

if (fs.existsSync(envExample) && !fs.existsSync(envFile)) {
  fs.copyFileSync(envExample, envFile);
  console.log('Successfully created .env from .env.example');
} else {
  console.log('.env file already exists or .env.example missing.');
}
