#!/usr/bin/env node

/**
 * Production Build Script
 *
 * This script optimizes all assets for production deployment:
 * - Minifies JavaScript files
 * - Minifies CSS files
 * - Minifies HTML files
 * - Generates source maps for debugging
 * - Creates a /dist directory with optimized assets
 *
 * Performance Impact:
 * - JavaScript: 40-60% size reduction
 * - CSS: 30-50% size reduction
 * - HTML: 10-20% size reduction
 * - Combined with gzip: 70-85% total reduction
 *
 * Usage:
 *   node build.js
 *   npm run build
 *
 * Output:
 *   /dist - Production-ready optimized files
 *
 * @module BuildScript
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const rootDir = __dirname;
const distDir = path.join(rootDir, 'dist');
const jsDir = path.join(rootDir, 'js');

console.log('🏗️  Starting production build...\n');

/**
 * Create dist directory if it doesn't exist
 */
function ensureDistDirectory() {
    if (!fs.existsSync(distDir)) {
        fs.mkdirSync(distDir, { recursive: true });
        console.log('✅ Created /dist directory');
    }

    // Create subdirectories
    const subdirs = ['js', 'css', 'data'];
    subdirs.forEach(dir => {
        const dirPath = path.join(distDir, dir);
        if (!fs.existsSync(dirPath)) {
            fs.mkdirSync(dirPath, { recursive: true });
        }
    });
}

/**
 * Minify JavaScript files using Terser
 */
function minifyJavaScript() {
    console.log('📦 Minifying JavaScript files...');

    if (!fs.existsSync(jsDir)) {
        console.log('⚠️  No /js directory found, skipping JS minification');
        return;
    }

    const jsFiles = fs.readdirSync(jsDir).filter(file => file.endsWith('.js'));

    if (jsFiles.length === 0) {
        console.log('⚠️  No JavaScript files found in /js');
        return;
    }

    jsFiles.forEach(file => {
        const inputPath = path.join(jsDir, file);
        const outputPath = path.join(distDir, 'js', file);
        const stats = fs.statSync(inputPath);
        const originalSize = stats.size;

        try {
            // Terser options for optimal compression
            execSync(`npx terser ${inputPath} -o ${outputPath} --compress --mangle --source-map "url=${file}.map" --comments false`, {
                stdio: 'inherit'
            });

            const newStats = fs.statSync(outputPath);
            const newSize = newStats.size;
            const reduction = ((1 - newSize / originalSize) * 100).toFixed(1);

            console.log(`   ✓ ${file}: ${formatBytes(originalSize)} → ${formatBytes(newSize)} (-${reduction}%)`);
        } catch (error) {
            console.error(`   ✗ Error minifying ${file}:`, error.message);
        }
    });
}

/**
 * Minify CSS files using clean-css
 */
function minifyCSS() {
    console.log('\n🎨 Minifying CSS files...');

    const cssFiles = fs.readdirSync(rootDir).filter(file => file.endsWith('.css'));

    if (cssFiles.length === 0) {
        console.log('⚠️  No CSS files found');
        return;
    }

    cssFiles.forEach(file => {
        const inputPath = path.join(rootDir, file);
        const outputPath = path.join(distDir, 'css', file);
        const stats = fs.statSync(inputPath);
        const originalSize = stats.size;

        try {
            execSync(`npx cleancss -o ${outputPath} ${inputPath}`, {
                stdio: 'inherit'
            });

            const newStats = fs.statSync(outputPath);
            const newSize = newStats.size;
            const reduction = ((1 - newSize / originalSize) * 100).toFixed(1);

            console.log(`   ✓ ${file}: ${formatBytes(originalSize)} → ${formatBytes(newSize)} (-${reduction}%)`);
        } catch (error) {
            console.error(`   ✗ Error minifying ${file}:`, error.message);
        }
    });
}

/**
 * Minify HTML files using html-minifier-terser
 */
function minifyHTML() {
    console.log('\n📄 Minifying HTML files...');

    const htmlFiles = fs.readdirSync(rootDir).filter(file =>
        file.endsWith('.html') && !file.includes('backup')
    );

    if (htmlFiles.length === 0) {
        console.log('⚠️  No HTML files found');
        return;
    }

    htmlFiles.forEach(file => {
        const inputPath = path.join(rootDir, file);
        const outputPath = path.join(distDir, file);
        const stats = fs.statSync(inputPath);
        const originalSize = stats.size;

        try {
            // html-minifier options for aggressive minification
            execSync(`npx html-minifier-terser \
                --collapse-whitespace \
                --remove-comments \
                --remove-redundant-attributes \
                --remove-script-type-attributes \
                --remove-tag-whitespace \
                --use-short-doctype \
                --minify-css true \
                --minify-js true \
                -o ${outputPath} \
                ${inputPath}`, {
                stdio: 'inherit'
            });

            const newStats = fs.statSync(outputPath);
            const newSize = newStats.size;
            const reduction = ((1 - newSize / originalSize) * 100).toFixed(1);

            console.log(`   ✓ ${file}: ${formatBytes(originalSize)} → ${formatBytes(newSize)} (-${reduction}%)`);
        } catch (error) {
            console.error(`   ✗ Error minifying ${file}:`, error.message);
        }
    });
}

/**
 * Copy static assets (images, fonts, etc.)
 */
function copyStaticAssets() {
    console.log('\n📋 Copying static assets...');

    const assetExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot'];
    const files = fs.readdirSync(rootDir);

    let copiedCount = 0;

    files.forEach(file => {
        const ext = path.extname(file);
        if (assetExtensions.includes(ext)) {
            const sourcePath = path.join(rootDir, file);
            const destPath = path.join(distDir, file);

            fs.copyFileSync(sourcePath, destPath);
            copiedCount++;
            console.log(`   ✓ Copied ${file}`);
        }
    });

    if (copiedCount === 0) {
        console.log('   ℹ️  No static assets to copy');
    }
}

/**
 * Copy server.js to dist (no minification to preserve readability)
 */
function copyServerFiles() {
    console.log('\n🖥️  Copying server files...');

    const serverFiles = ['server.js', 'package.json', 'package-lock.json'];

    serverFiles.forEach(file => {
        const sourcePath = path.join(rootDir, file);
        if (fs.existsSync(sourcePath)) {
            const destPath = path.join(distDir, file);
            fs.copyFileSync(sourcePath, destPath);
            console.log(`   ✓ Copied ${file}`);
        }
    });
}

/**
 * Generate build report
 */
function generateBuildReport() {
    console.log('\n📊 Build Report:\n');

    const distSize = getDirectorySize(distDir);
    const sourceSize = getDirectorySize(rootDir, ['node_modules', 'dist', '.git', 'data', 'backups', 'test-results', 'playwright-report']);

    console.log(`   Source Size:      ${formatBytes(sourceSize)}`);
    console.log(`   Optimized Size:   ${formatBytes(distSize)}`);
    console.log(`   Size Reduction:   ${formatBytes(sourceSize - distSize)} (${((1 - distSize / sourceSize) * 100).toFixed(1)}%)`);
    console.log(`\n   Output Directory: ${distDir}`);
    console.log(`\n✨ Build completed successfully!\n`);
}

/**
 * Format bytes to human-readable string
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Get total size of directory
 */
function getDirectorySize(dir, excludeDirs = []) {
    let totalSize = 0;

    function calculateSize(currentPath) {
        const stats = fs.statSync(currentPath);

        if (stats.isDirectory()) {
            const dirName = path.basename(currentPath);
            if (excludeDirs.includes(dirName)) {
                return;
            }

            const files = fs.readdirSync(currentPath);
            files.forEach(file => {
                calculateSize(path.join(currentPath, file));
            });
        } else {
            totalSize += stats.size;
        }
    }

    calculateSize(dir);
    return totalSize;
}

/**
 * Main build process
 */
function build() {
    try {
        ensureDistDirectory();
        minifyJavaScript();
        minifyCSS();
        minifyHTML();
        copyStaticAssets();
        copyServerFiles();
        generateBuildReport();
    } catch (error) {
        console.error('\n❌ Build failed:', error.message);
        process.exit(1);
    }
}

// Run build
build();
