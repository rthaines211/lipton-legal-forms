# Phase 7: Integration & Deployment

## Overview
Integrate the Python discovery processor with the existing Node.js server, update database schema, create API endpoints, and deploy the complete system.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Submits Form                      │
│                        (index.html)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Node.js Server (server.js)                │
│  - Receives form POST                                         │
│  - Transforms to goalOutput.md format                         │
│  - Saves to PostgreSQL (existing flow)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Discovery Processor (NEW)                │
│  Phase 1: Normalize form data                                │
│  Phase 2: Build HoH × Defendant datasets                     │
│  Phase 3: Generate 180+ flags                                │
│  Phase 4: Apply document profiles                            │
│  Phase 5: Split into sets                                    │
│  Phase 6: Generate output (Zapier + Local)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                PostgreSQL Database (UPDATED)                 │
│  - Cases table (existing)                                    │
│  - Parties table (existing)                                  │
│  - Discovery datasets table (NEW)                            │
│  - Discovery sets table (NEW)                                │
│  - Document generations table (NEW)                          │
└─────────────────────────────────────────────────────────────┘
```

## Task 7.1: Database Schema Updates
**File**: `database/schema_updates_phase7.sql`

```sql
-- ============================================================================
-- Phase 7: Discovery Processing Tables
-- ============================================================================

-- Discovery Datasets Table
-- Stores enriched datasets (HoH × Defendant combinations) with 180+ flags
CREATE TABLE discovery_datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,

    -- References to parties
    plaintiff_id UUID NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    defendant_id UUID NOT NULL REFERENCES parties(id) ON DELETE CASCADE,

    -- Dataset metadata
    dataset_id VARCHAR(255) UNIQUE NOT NULL,

    -- Flags (JSONB for flexibility)
    flags JSONB NOT NULL,

    -- Discovery data (original arrays)
    discovery_data JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT discovery_datasets_plaintiff_defendant_unique
        UNIQUE (case_id, plaintiff_id, defendant_id)
);

-- Discovery Sets Table
-- Stores split sets for document generation
CREATE TABLE discovery_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES discovery_datasets(id) ON DELETE CASCADE,

    -- Document profile
    doc_type VARCHAR(50) NOT NULL CHECK (doc_type IN ('SROGs', 'PODs', 'Admissions')),
    template_name VARCHAR(255) NOT NULL,

    -- Set information
    set_number INTEGER NOT NULL,
    total_sets INTEGER NOT NULL,
    interrogatory_start INTEGER NOT NULL,
    interrogatory_end INTEGER NOT NULL,
    total_interrogatories INTEGER NOT NULL,
    is_first_set BOOLEAN NOT NULL,

    -- Filename for generation
    filename VARCHAR(511) NOT NULL,

    -- Set flags (subset of dataset flags)
    set_flags JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT discovery_sets_dataset_doctype_set_unique
        UNIQUE (dataset_id, doc_type, set_number)
);

-- Document Generations Table
-- Tracks generated Word documents
CREATE TABLE document_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    set_id UUID NOT NULL REFERENCES discovery_sets(id) ON DELETE CASCADE,

    -- Generation metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(255),

    -- File information
    file_path TEXT,
    file_size_bytes BIGINT,

    -- Generation status
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'generating', 'completed', 'failed')),
    error_message TEXT,

    -- Zapier integration
    zapier_webhook_sent BOOLEAN DEFAULT false,
    zapier_response JSONB
);

-- Indexes for performance
CREATE INDEX idx_discovery_datasets_case ON discovery_datasets(case_id);
CREATE INDEX idx_discovery_datasets_plaintiff ON discovery_datasets(plaintiff_id);
CREATE INDEX idx_discovery_datasets_defendant ON discovery_datasets(defendant_id);
CREATE INDEX idx_discovery_sets_dataset ON discovery_sets(dataset_id);
CREATE INDEX idx_discovery_sets_doctype ON discovery_sets(doc_type);
CREATE INDEX idx_document_generations_set ON document_generations(set_id);
CREATE INDEX idx_document_generations_status ON document_generations(status);

-- Triggers
CREATE TRIGGER update_discovery_datasets_updated_at BEFORE UPDATE ON discovery_datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE discovery_datasets IS 'Stores enriched datasets with 180+ flags for discovery processing';
COMMENT ON TABLE discovery_sets IS 'Stores split sets with max 120 interrogatories each';
COMMENT ON TABLE document_generations IS 'Tracks generated discovery documents';
```

## Task 7.2: Python-Node.js Integration
**File**: `normalization work/src/integration/node_bridge.py`

```python
import sys
import json
from pathlib import Path

# Import all phases
from phase1.normalizer import normalize_form_data
from phase2.dataset_builder import build_datasets
from phase3.flag_pipeline import FlagProcessorPipeline
from phase4.profile_pipeline import ProfilePipeline
from phase5.splitting_pipeline import SplittingPipeline
from phase6.output_generator import OutputGenerator, OutputMode

def process_form_submission(form_json: dict) -> dict:
    """
    Main entry point for processing form submission.

    This function is called by Node.js server via subprocess.

    Args:
        form_json: Raw form JSON from server.js

    Returns:
        Dictionary with Zapier and Local outputs
    """
    try:
        # Phase 1: Normalize
        normalized = normalize_form_data(form_json)

        # Phase 2: Build datasets
        datasets = build_datasets(normalized)

        # Phase 3: Generate flags
        flag_pipeline = FlagProcessorPipeline()
        enriched = flag_pipeline.process_all_datasets(datasets)

        # Phase 4: Apply profiles
        profile_pipeline = ProfilePipeline()
        profiled = profile_pipeline.apply_profiles_to_collection(enriched)

        # Phase 5: Split into sets
        splitting_pipeline = SplittingPipeline()
        split_results = splitting_pipeline.split_all_datasets(profiled)

        # Phase 6: Generate output
        output_generator = OutputGenerator()
        output = output_generator.generate_output(split_results, OutputMode.BOTH)

        return {
            'success': True,
            'output': output,
            'metadata': {
                'datasets_processed': len(datasets['datasets']),
                'total_sets': len(output['zapier']['all_sets'])
            }
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def main():
    """CLI entry point for Node.js integration."""
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': 'No input provided'}))
        sys.exit(1)

    # Read input JSON from command line argument
    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        form_json = json.load(f)

    # Process
    result = process_form_submission(form_json)

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)

if __name__ == '__main__':
    main()
```

## Task 7.3: Node.js API Endpoints
**File**: `server.js` (additions)

```javascript
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;
const os = require('os');

/**
 * Process form data through Python discovery processor
 */
async function processDiscovery(formData, caseId) {
    return new Promise((resolve, reject) => {
        // Create temp file for input
        const tempFile = path.join(os.tmpdir(), `form-${caseId}.json`);

        // Write form data to temp file
        fs.writeFile(tempFile, JSON.stringify(formData))
            .then(() => {
                // Spawn Python process
                const python = spawn('python3', [
                    path.join(__dirname, 'normalization work/src/integration/node_bridge.py'),
                    tempFile
                ]);

                let stdout = '';
                let stderr = '';

                python.stdout.on('data', (data) => {
                    stdout += data.toString();
                });

                python.stderr.on('data', (data) => {
                    stderr += data.toString();
                });

                python.on('close', async (code) => {
                    // Clean up temp file
                    await fs.unlink(tempFile).catch(() => {});

                    if (code === 0) {
                        try {
                            const result = JSON.parse(stdout);
                            resolve(result);
                        } catch (e) {
                            reject(new Error(`Failed to parse Python output: ${e.message}`));
                        }
                    } else {
                        reject(new Error(`Python process failed: ${stderr}`));
                    }
                });
            })
            .catch(reject);
    });
}

/**
 * POST /api/discovery/process
 * Process form data through discovery pipeline
 */
app.post('/api/discovery/process', async (req, res) => {
    try {
        const formData = req.body;
        const caseId = formData.id;

        console.log(`🔄 Processing discovery for case: ${caseId}`);

        // Process through Python pipeline
        const result = await processDiscovery(formData, caseId);

        if (!result.success) {
            return res.status(500).json({
                success: false,
                error: 'Discovery processing failed',
                details: result.error
            });
        }

        // Save to database
        await saveDiscoveryToDatabase(result.output, caseId);

        res.json({
            success: true,
            message: 'Discovery processed successfully',
            metadata: result.metadata,
            output: result.output
        });

    } catch (error) {
        console.error('❌ Error processing discovery:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            details: error.message
        });
    }
});

/**
 * Save discovery output to database
 */
async function saveDiscoveryToDatabase(output, caseId) {
    const client = await pool.connect();

    try {
        await client.query('BEGIN');

        // Save datasets and sets
        // (Implementation details...)

        await client.query('COMMIT');

    } catch (error) {
        await client.query('ROLLBACK');
        throw error;
    } finally {
        client.release();
    }
}
```

## Task 7.4: End-to-End Testing
**File**: `tests/integration/test_end_to_end.py`

```python
def test_full_pipeline_goaloutput_example():
    """Test complete pipeline with goalOutput.md example"""
    # Load goalOutput.md
    form_json = load_fixture('goaloutput_example.json')

    # Run full pipeline
    result = process_form_submission(form_json)

    # Verify success
    assert result['success'] == True

    # Verify output structure
    output = result['output']
    assert 'zapier' in output
    assert 'local' in output

    # Verify Zapier output
    assert 'all_sets' in output['zapier']
    assert len(output['zapier']['all_sets']) > 0

    # Verify Local output
    assert 'documents' in output['local']
    assert len(output['local']['documents']) == 3  # SROGs, PODs, Admissions

    # Verify metadata
    metadata = result['metadata']
    assert metadata['datasets_processed'] == 6  # 3 HoH × 2 defendants
    assert metadata['total_sets'] > 0
```

## Task 7.5: Documentation

### API Documentation
**File**: `normalization work/API.md`

```markdown
# Discovery Processor API

## POST /api/discovery/process

Process form submission through discovery pipeline.

### Request Body
```json
{
  "id": "form-entry-1729123456789",
  "plaintiff-1-first-name": "John",
  ...all form fields...
}
```

### Response
```json
{
  "success": true,
  "metadata": {
    "datasets_processed": 6,
    "total_sets": 18
  },
  "output": {
    "zapier": {...},
    "local": {...}
  }
}
```

## GET /api/discovery/sets/:case_id

Retrieve all discovery sets for a case.

## GET /api/discovery/download/:set_id

Download generated document for a set.
```

### Deployment Guide
**File**: `normalization work/DEPLOYMENT.md`

```markdown
# Deployment Guide

## Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+

## Installation Steps

1. Install Python dependencies:
```bash
cd "normalization work"
pip install -r requirements.txt
```

2. Run database migrations:
```bash
psql legal_forms_db < database/schema_updates_phase7.sql
```

3. Test Python integration:
```bash
python src/integration/node_bridge.py test_input.json
```

4. Restart Node.js server:
```bash
npm start
```

## Verification
- Submit test form
- Check `/api/discovery/process` endpoint
- Verify database tables populated
```

## Test Plan

### Test 7.1: Python-Node.js Bridge
**File**: `tests/integration/test_node_bridge.py`

```python
def test_bridge_processes_valid_input():
    """Test bridge processes valid form JSON"""
    form_json = create_test_form_json()
    result = process_form_submission(form_json)

    assert result['success'] == True
    assert 'output' in result

def test_bridge_handles_invalid_input():
    """Test bridge handles errors gracefully"""
    invalid_json = {}
    result = process_form_submission(invalid_json)

    assert result['success'] == False
    assert 'error' in result
```

### Test 7.2: Database Integration
**File**: `tests/integration/test_database_integration.py`

```python
async def test_save_discovery_to_database():
    """Test saving discovery output to database"""
    output = create_test_output()
    case_id = 'test-case-123'

    await saveDiscoveryToDatabase(output, case_id)

    # Verify datasets saved
    datasets = await query_discovery_datasets(case_id)
    assert len(datasets) > 0

    # Verify sets saved
    sets = await query_discovery_sets(case_id)
    assert len(sets) > 0
```

### Test 7.3: API Endpoints
**File**: `tests/integration/test_api_endpoints.js`

```javascript
describe('Discovery API Endpoints', () => {
    it('should process discovery via POST /api/discovery/process', async () => {
        const formData = loadTestFormData();

        const response = await request(app)
            .post('/api/discovery/process')
            .send(formData)
            .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.output).toBeDefined();
    });
});
```

## Exit Criteria

### Integration Complete
- ✅ Python-Node.js bridge working
- ✅ Database schema updated
- ✅ API endpoints functional

### All Tests Pass
- ✅ End-to-end tests pass
- ✅ Integration tests pass
- ✅ API tests pass

### Documentation Complete
- ✅ API documentation written
- ✅ Deployment guide written
- ✅ Troubleshooting guide written

### Performance
- ✅ Process case in < 5 seconds
- ✅ Database queries optimized
- ✅ Memory usage acceptable

### Deployment
- ✅ Staging environment tested
- ✅ Production deployment successful
- ✅ Monitoring in place

## Deliverables
1. ✅ Database schema updates
2. ✅ Python-Node.js bridge
3. ✅ API endpoints
4. ✅ End-to-end tests
5. ✅ Documentation
6. ✅ Deployment guide

---

**Phase Status**: 📋 Planning
**Estimated Duration**: 3-5 days
**Previous Phase**: [Phase 6: Output Generation](PHASE-6-OUTPUT-GENERATION.md)
**Completion**: Project Complete! 🎉
