// ========================================
// Choose Me Auto - Browser Diagnostic Script
// ========================================
// 
// INSTRUCTIONS:
// 1. Open https://autodealership.preview.emergentagent.com/
// 2. Right-click → Inspect → Console tab
// 3. Copy and paste this entire script
// 4. Press Enter to run
// 5. Share the output with Emergent support
//
// ========================================

console.clear();
console.log('🚗 Choose Me Auto - Diagnostic Starting...\n');

async function runDiagnostics() {
    const results = {
        apiVehicles: null,
        apiSingleVehicle: null,
        imageTest: null,
        networkRequests: null
    };

    // Test 1: API - List all vehicles
    console.log('Test 1: Checking /api/vehicles endpoint...');
    try {
        const response = await fetch('/api/vehicles');
        results.apiVehicles = {
            status: response.status,
            ok: response.ok,
            url: response.url
        };
        
        if (response.ok) {
            const data = await response.json();
            results.apiVehicles.count = data.length;
            results.apiVehicles.sample = data[0];
            console.log(`✅ API Works! Found ${data.length} vehicles`);
            console.log('   Sample vehicle:', data[0]);
        } else {
            console.error(`❌ API Failed: ${response.status} ${response.statusText}`);
            console.error('   URL:', response.url);
        }
    } catch (error) {
        console.error('❌ API Request Failed:', error.message);
        results.apiVehicles = { error: error.message };
    }
    console.log('');

    // Test 2: API - Single vehicle
    console.log('Test 2: Checking /api/vehicles/P57801 endpoint...');
    try {
        const response = await fetch('/api/vehicles/P57801');
        results.apiSingleVehicle = {
            status: response.status,
            ok: response.ok,
            url: response.url
        };
        
        if (response.ok) {
            const data = await response.json();
            results.apiSingleVehicle.vehicle = data;
            console.log('✅ Single Vehicle API Works!');
            console.log('   Vehicle:', `${data.year} ${data.make} ${data.model}`);
            console.log('   Image URL:', data.image_url);
            console.log('   Additional Images:', data.image_urls?.length || 0);
        } else {
            console.error(`❌ Single Vehicle API Failed: ${response.status} ${response.statusText}`);
        }
    } catch (error) {
        console.error('❌ Single Vehicle Request Failed:', error.message);
        results.apiSingleVehicle = { error: error.message };
    }
    console.log('');

    // Test 3: Image loading
    console.log('Test 3: Checking /vehicles/P57801_1.jpg image...');
    try {
        const response = await fetch('/vehicles/P57801_1.jpg');
        results.imageTest = {
            status: response.status,
            ok: response.ok,
            url: response.url,
            contentType: response.headers.get('content-type'),
            size: response.headers.get('content-length')
        };
        
        if (response.ok) {
            console.log('✅ Image Works!');
            console.log('   Content-Type:', response.headers.get('content-type'));
            console.log('   Size:', response.headers.get('content-length'), 'bytes');
        } else {
            console.error(`❌ Image Failed: ${response.status} ${response.statusText}`);
        }
    } catch (error) {
        console.error('❌ Image Request Failed:', error.message);
        results.imageTest = { error: error.message };
    }
    console.log('');

    // Test 4: Check for localhost URLs
    console.log('Test 4: Checking for localhost API calls...');
    const perfEntries = performance.getEntriesByType('resource');
    const apiCalls = perfEntries.filter(entry => 
        entry.name.includes('/api/') || entry.name.includes('localhost')
    );
    
    results.networkRequests = apiCalls.map(entry => ({
        url: entry.name,
        duration: entry.duration,
        transferSize: entry.transferSize
    }));

    const localhostCalls = apiCalls.filter(entry => entry.name.includes('localhost'));
    if (localhostCalls.length > 0) {
        console.error('❌ FOUND LOCALHOST CALLS:');
        localhostCalls.forEach(call => {
            console.error('   ', call.name);
        });
    } else {
        console.log('✅ No localhost calls detected');
    }
    console.log('');

    // Summary
    console.log('========================================');
    console.log('📊 DIAGNOSTIC SUMMARY');
    console.log('========================================');
    console.log('');
    console.log('API /api/vehicles:', results.apiVehicles?.ok ? '✅ WORKING' : '❌ FAILED');
    console.log('API /api/vehicles/P57801:', results.apiSingleVehicle?.ok ? '✅ WORKING' : '❌ FAILED');
    console.log('Image /vehicles/P57801_1.jpg:', results.imageTest?.ok ? '✅ WORKING' : '❌ FAILED');
    console.log('Localhost calls:', localhostCalls.length > 0 ? '❌ FOUND' : '✅ NONE');
    console.log('');

    // Diagnosis
    console.log('========================================');
    console.log('🔍 DIAGNOSIS');
    console.log('========================================');
    console.log('');

    if (!results.apiVehicles?.ok) {
        console.log('❌ ISSUE: API endpoint not accessible');
        console.log('   Problem: /api/vehicles is not reachable');
        console.log('   Solution: Emergent needs to configure /api/* routing to FastAPI backend');
        console.log('');
    }

    if (!results.imageTest?.ok) {
        console.log('❌ ISSUE: Images not loading');
        console.log('   Problem: /vehicles/*.jpg files are not accessible');
        console.log('   Solution: Emergent needs to ensure frontend/public/vehicles/ is deployed');
        console.log('');
    }

    if (localhostCalls.length > 0) {
        console.log('❌ ISSUE: Frontend calling localhost');
        console.log('   Problem: API calls going to localhost instead of production URL');
        console.log('   Solution: Frontend environment variable REACT_APP_BACKEND_URL not set correctly');
        console.log('');
    }

    if (results.apiVehicles?.ok && results.imageTest?.ok) {
        console.log('✅ ALL TESTS PASSED!');
        console.log('   Everything should be working. If vehicles still not showing:');
        console.log('   1. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)');
        console.log('   2. Clear browser cache');
        console.log('   3. Check browser console for JavaScript errors');
        console.log('');
    }

    // Return results for copying
    return results;
}

// Run diagnostics
console.log('Starting diagnostics...\n');
runDiagnostics().then(results => {
    console.log('');
    console.log('========================================');
    console.log('✅ Diagnostic Complete!');
    console.log('========================================');
    console.log('');
    console.log('📋 Copy these results to share with support:');
    console.log(JSON.stringify(results, null, 2));
});
