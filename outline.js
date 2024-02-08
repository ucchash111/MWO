const fs = require('fs');
const path = require('path');

const LIB_PATH = path.resolve('./web_app'); // Use path.resolve to ensure the correct absolute path

console.log(`Reading directory: ${LIB_PATH}`);

function readDirectory(directory) {
  fs.readdir(directory, { withFileTypes: true }, (err, dirents) => {
    if (err) {
      console.error('Error reading directory:', directory, err);
      return;
    }

    dirents.forEach((dirent) => {
      const fullPath = path.join(directory, dirent.name);
      if (dirent.isDirectory()) {
        // Recurse into subdirectories
        readDirectory(fullPath);
      } else {
        // Process files based on extension
        const validExtensions = ['.py', '.html', '.dart'];
        const fileExtension = path.extname(dirent.name);
        if (validExtensions.includes(fileExtension)) {
          // Read file content
          fs.readFile(fullPath, 'utf8', (err, data) => {
            if (err) {
              console.error('Error reading file:', fullPath, err);
              return;
            }

            // For simplicity, this example just logs the content. 
            // You can add specific processing for each file type here.
            console.log(`File Name: ${fullPath}`);
            console.log(`Content:\n${data}`);
            console.log('--------------------------------');
          });
        }
      }
    });
  });
}

// Start reading from the lib directory
readDirectory(LIB_PATH);

