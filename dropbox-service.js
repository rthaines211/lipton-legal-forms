/**
 * Dropbox Service Module
 *
 * Handles all Dropbox API operations including file uploads and folder creation.
 * Preserves local folder structure when uploading to Dropbox.
 *
 * Configuration:
 * - DROPBOX_ACCESS_TOKEN: OAuth token for Dropbox API authentication
 * - DROPBOX_ENABLED: Enable/disable Dropbox uploads
 * - DROPBOX_BASE_PATH: Base folder path in Dropbox (e.g., /Apps/LegalFormApp)
 * - LOCAL_OUTPUT_PATH: Local output directory to mirror to Dropbox
 * - CONTINUE_ON_DROPBOX_FAILURE: Continue on upload failure
 *
 * Features:
 * - Automatic folder creation in Dropbox
 * - File overwriting (WriteMode.overwrite)
 * - Path mapping from local to Dropbox structure
 * - Comprehensive error handling and logging
 *
 * Example Usage:
 *   const dropboxService = require('./dropbox-service');
 *   await dropboxService.uploadFile('/output/Clients/Case1/file.pdf');
 *
 * Last Updated: 2025-10-20
 */

const { Dropbox } = require('dropbox');
const fs = require('fs').promises;
const path = require('path');

/**
 * Dropbox Configuration
 * Loaded from environment variables with sensible defaults
 */
const DROPBOX_CONFIG = {
    accessToken: process.env.DROPBOX_ACCESS_TOKEN || '',
    enabled: process.env.DROPBOX_ENABLED === 'true',
    basePath: process.env.DROPBOX_BASE_PATH || '/Apps/LegalFormApp',
    localOutputPath: process.env.LOCAL_OUTPUT_PATH || '/output',
    continueOnFailure: process.env.CONTINUE_ON_DROPBOX_FAILURE !== 'false'
};

// Initialize Dropbox client if enabled and token is provided
let dbx = null;
if (DROPBOX_CONFIG.enabled && DROPBOX_CONFIG.accessToken) {
    dbx = new Dropbox({ accessToken: DROPBOX_CONFIG.accessToken });
    console.log('✅ Dropbox service initialized');
    console.log(`   Base path: ${DROPBOX_CONFIG.basePath}`);
} else {
    if (DROPBOX_CONFIG.enabled && !DROPBOX_CONFIG.accessToken) {
        console.warn('⚠️  Dropbox enabled but no access token provided. Uploads will be skipped.');
    } else {
        console.log('ℹ️  Dropbox service disabled');
    }
}

/**
 * Maps a local file path to its corresponding Dropbox path
 *
 * @param {string} localPath - Local file path (e.g., /output/Clients/Case1/file.pdf)
 * @returns {string} Dropbox path (e.g., /Apps/LegalFormApp/Clients/Case1/file.pdf)
 *
 * @example
 * mapLocalPathToDropbox('/output/Clients/Case1/file.pdf')
 * // Returns: '/Apps/LegalFormApp/Clients/Case1/file.pdf'
 */
function mapLocalPathToDropbox(localPath) {
    // Normalize paths to use forward slashes
    const normalizedLocal = localPath.replace(/\\/g, '/');
    const normalizedOutputPath = DROPBOX_CONFIG.localOutputPath.replace(/\\/g, '/');

    // Remove the local output path prefix
    let relativePath = normalizedLocal;
    if (normalizedLocal.startsWith(normalizedOutputPath)) {
        relativePath = normalizedLocal.substring(normalizedOutputPath.length);
    }

    // Ensure relative path starts with /
    if (!relativePath.startsWith('/')) {
        relativePath = '/' + relativePath;
    }

    // Combine base path with relative path
    let dropboxPath = DROPBOX_CONFIG.basePath + relativePath;

    // Ensure no double slashes
    dropboxPath = dropboxPath.replace(/\/+/g, '/');

    return dropboxPath;
}

/**
 * Creates a folder in Dropbox if it doesn't exist
 *
 * @param {string} folderPath - Dropbox folder path to create
 * @returns {Promise<boolean>} True if folder exists or was created successfully
 *
 * @example
 * await ensureFolderExists('/Apps/LegalFormApp/Clients/Case1')
 */
async function ensureFolderExists(folderPath) {
    if (!dbx) {
        return false;
    }

    try {
        // Check if folder exists by getting its metadata
        await dbx.filesGetMetadata({ path: folderPath });
        return true; // Folder exists
    } catch (error) {
        if (error.status === 409) {
            // Folder doesn't exist, try to create it
            try {
                await dbx.filesCreateFolderV2({
                    path: folderPath,
                    autorename: false
                });
                console.log(`📁 Created Dropbox folder: ${folderPath}`);
                return true;
            } catch (createError) {
                console.error(`❌ Failed to create Dropbox folder ${folderPath}:`, createError.message);
                return false;
            }
        } else {
            console.error(`❌ Error checking Dropbox folder ${folderPath}:`, error.message);
            return false;
        }
    }
}

/**
 * Recursively creates all parent folders for a given path
 *
 * @param {string} dropboxPath - Full Dropbox file path
 * @returns {Promise<boolean>} True if all folders exist or were created
 *
 * @example
 * await ensureParentFoldersExist('/Apps/LegalFormApp/Clients/Case1/SROGs/file.pdf')
 * // Creates: /Apps/LegalFormApp, /Apps/LegalFormApp/Clients,
 * //          /Apps/LegalFormApp/Clients/Case1, /Apps/LegalFormApp/Clients/Case1/SROGs
 */
async function ensureParentFoldersExist(dropboxPath) {
    if (!dbx) {
        return false;
    }

    const pathParts = dropboxPath.split('/').filter(part => part.length > 0);

    // Build folder paths incrementally
    let currentPath = '';
    for (let i = 0; i < pathParts.length - 1; i++) { // -1 to exclude the filename
        currentPath += '/' + pathParts[i];

        // Skip if it's just the base path (usually already exists)
        if (currentPath === DROPBOX_CONFIG.basePath) {
            continue;
        }

        const folderExists = await ensureFolderExists(currentPath);
        if (!folderExists && !DROPBOX_CONFIG.continueOnFailure) {
            return false;
        }
    }

    return true;
}

/**
 * Uploads a file to Dropbox, preserving the folder structure
 *
 * @param {string} localFilePath - Absolute local file path
 * @param {Buffer|string} fileContent - File content (optional, will read from disk if not provided)
 * @returns {Promise<object>} Upload result with status and paths
 *
 * @example
 * const result = await uploadFile('/output/Clients/Case1/file.pdf');
 * console.log(result);
 * // {
 * //   success: true,
 * //   localPath: '/output/Clients/Case1/file.pdf',
 * //   dropboxPath: '/Apps/LegalFormApp/Clients/Case1/file.pdf'
 * // }
 */
async function uploadFile(localFilePath, fileContent = null) {
    const result = {
        success: false,
        localPath: localFilePath,
        dropboxPath: null,
        error: null
    };

    // Check if Dropbox is enabled and configured
    if (!DROPBOX_CONFIG.enabled) {
        result.error = 'Dropbox is disabled';
        return result;
    }

    if (!dbx) {
        result.error = 'Dropbox client not initialized';
        return result;
    }

    try {
        // Map local path to Dropbox path
        const dropboxPath = mapLocalPathToDropbox(localFilePath);
        result.dropboxPath = dropboxPath;

        // Ensure parent folders exist
        const foldersCreated = await ensureParentFoldersExist(dropboxPath);
        if (!foldersCreated && !DROPBOX_CONFIG.continueOnFailure) {
            result.error = 'Failed to create parent folders';
            return result;
        }

        // Read file content if not provided
        let contents = fileContent;
        if (!contents) {
            contents = await fs.readFile(localFilePath);
        }

        // Upload file to Dropbox (overwrite if exists)
        await dbx.filesUpload({
            path: dropboxPath,
            contents: contents,
            mode: { '.tag': 'overwrite' },
            autorename: false,
            mute: false,
            strict_conflict: false
        });

        result.success = true;
        console.log(`☁️  Uploaded to Dropbox: ${localFilePath} → ${dropboxPath}`);

        return result;

    } catch (error) {
        result.error = error.message;
        console.error(`❌ Dropbox upload failed for ${localFilePath}:`, error.message);

        if (!DROPBOX_CONFIG.continueOnFailure) {
            throw error;
        }

        return result;
    }
}

/**
 * Uploads multiple files to Dropbox in parallel
 *
 * @param {string[]} localFilePaths - Array of absolute local file paths
 * @returns {Promise<object[]>} Array of upload results
 *
 * @example
 * const results = await uploadFiles([
 *   '/output/Clients/Case1/file1.pdf',
 *   '/output/Clients/Case1/file2.pdf'
 * ]);
 */
async function uploadFiles(localFilePaths) {
    if (!DROPBOX_CONFIG.enabled || !dbx) {
        console.log('ℹ️  Dropbox disabled, skipping batch upload');
        return localFilePaths.map(path => ({
            success: false,
            localPath: path,
            dropboxPath: null,
            error: 'Dropbox is disabled'
        }));
    }

    console.log(`📤 Uploading ${localFilePaths.length} files to Dropbox...`);

    const uploadPromises = localFilePaths.map(filePath => uploadFile(filePath));
    const results = await Promise.allSettled(uploadPromises);

    const successCount = results.filter(r => r.status === 'fulfilled' && r.value.success).length;
    console.log(`✅ Successfully uploaded ${successCount}/${localFilePaths.length} files to Dropbox`);

    return results.map(r => r.status === 'fulfilled' ? r.value : { success: false, error: r.reason });
}

/**
 * Gets Dropbox account information (useful for testing connection)
 *
 * @returns {Promise<object>} Account information
 */
async function getAccountInfo() {
    if (!dbx) {
        throw new Error('Dropbox client not initialized');
    }

    try {
        const response = await dbx.usersGetCurrentAccount();
        return response.result;
    } catch (error) {
        console.error('❌ Failed to get Dropbox account info:', error.message);
        throw error;
    }
}

module.exports = {
    uploadFile,
    uploadFiles,
    mapLocalPathToDropbox,
    getAccountInfo,
    isEnabled: () => DROPBOX_CONFIG.enabled && dbx !== null,
    config: DROPBOX_CONFIG
};
