<?php

use App\Http\Controllers\JobMatchingController;

Route::get('/', [JobMatchingController::class, 'index'])->name('home');
Route::post('/upload-cv', [JobMatchingController::class, 'uploadCV'])->name('upload.cv');
Route::post('/filter-jobs', [JobMatchingController::class, 'filterJobs'])->name('filter.jobs');

// API routes that proxy to FastAPI
Route::get('/api/provinces', [JobMatchingController::class, 'getProvinces'])->name('api.provinces');
Route::get('/api/districts/{provinceCode}', [JobMatchingController::class, 'getDistricts'])->name('api.districts');
Route::get('/api/recent_jobs', [JobMatchingController::class, 'getMostRecentJobs'])->name('api.recent_jobs');