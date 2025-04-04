<?php

namespace App\Http\Controllers;

use App\Services\JobMatchingService;

use Illuminate\Http\Request;

class JobMatchingController extends Controller
{
    private $jobMatchingService;

    public function __construct(JobMatchingService $service)
    {
        $this->jobMatchingService = $service;
    }

    public function index()
    {
        $provinces = $this->jobMatchingService->getProvinces();
        return view('job-matching.index', compact('provinces'));
    }

    public function uploadCV(Request $request)
    {
        $request->validate([
            'cv' => 'required|file|mimes:pdf|max:10240',
        ]);

        $html = $this->jobMatchingService->uploadCV($request->file('cv'));
        // Store CV ID in session for later use
        if (preg_match('/<input[^>]*id="cv_id"[^>]*value="([^"]*)"/', $html, $matches)) {
            session(['cv_id' => $matches[1]]);
        }

        return view('job-matching.results', ['results' => $html]);
    }

    public function filterJobs(Request $request)
    {
        $filters = $request->all();
        // Add CV ID from session if not provided
        if (empty($filters['cv_id']) && session('cv_id')) {
            $filters['cv_id'] = session('cv_id');
        }
        \Log::info('Sending filter request:', $filters);
        $html = $this->jobMatchingService->filterJobs($filters);

        return view('job-matching.results', ['results' => $html]);
    }

    public function getProvinces()
    {
        $provinces = $this->jobMatchingService->getProvinces();
        return $provinces;
    }

    public function getDistricts($provinceCode)
    {
        $districts = $this->jobMatchingService->getDistricts($provinceCode);
        return $districts;
    }


    public function getMostRecentJobs($num_jobs = 200) {
        $jobs = $this->jobMatchingService->getMostRecentJobs($num_jobs);
        return $jobs;
    }
}