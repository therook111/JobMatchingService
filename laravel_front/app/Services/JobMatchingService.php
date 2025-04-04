<?php

namespace App\Services;
use App\Services\ElasticSearchService;

use Illuminate\Support\Facades\Http;

class JobMatchingService
{
    private $baseUrl;
    private $elasticService;

    public function __construct(ElasticSearchService $elasticService)
    {
        $this->baseUrl = env('FASTAPI_BASE_URL', 'http://localhost:5000');
        $this->elasticService = $elasticService;
    }

    public function uploadCV($file)
    {
        $response = Http::attach('CV', file_get_contents($file), $file->getClientOriginalName())
            ->post("{$this->baseUrl}/upload");

        return $response->body(); // Return the HTML response from FastAPI
    }

    public function filterJobs($filters)
{
    $response = Http::post("{$this->baseUrl}/filtering", $filters);
    

    // Fall back to returning the whole response if not JSON or no 'response' key
    return $response->body();
}

    public function getProvinces()
    {
        $params = [
            'index' => 'location',
            'body' => [
                '_source' => ['provinceID', 'provinceName'],
                'collapse' => [
                    'field' => 'provinceID'
                ],
                'size' => 1000
            ]
        ];

        $response = $this->elasticService->client->search($params);

        $documents = array_map(function($hit) {
            return [
                "code" => $hit['_source']['provinceID'],
                "name" => $hit['_source']['provinceName']
            ];
        }, $response['hits']['hits']);

        return json_encode($documents);
    }

    public function getDistricts($provinceCode)
    {
        $params = [
            'index' => 'location',
            'body' => [
                'query' => [
                'term' => [
                    'provinceID' => $provinceCode
                ]
            ],
            '_source' => ['districtID', 'districtName'],
            'size' => 100
        ]
        ];

        $response = $this->elasticService->client->search($params);
        $documents = array_map(function($hit) {
            return [
                "code" => $hit['_source']['districtID'],
                "name" => $hit['_source']['districtName']
            ];
        }, $response['hits']['hits']);

        return json_encode($documents);
    }

    public function getMostRecentJobs($num_jobs = 200) {
        $params_jobs = [
            'index' => 'jobs',
            'body' => [
                'query' => [
                    'match_all' => new \stdClass()
                ],
                'sort' => [
                    ['date_processed' => ['order' => 'desc']]
                ],
                '_source' => [
                    "JOB_ID", "title", "location_primary", "location_secondary", 
                    "date_processed", "salary_min", "salary_max", "deadline", "sectorID"
                ],
                'size' => $num_jobs
            ]
        ];

        $sectorsHashTable = $this->getSectors();
        
        $response = $this->elasticService->client->search($params_jobs);
        $documents = array_map(function($hit) use ($sectorsHashTable) {
            return [
                "id" => $hit['_source']['JOB_ID'],
                "title" => $hit['_source']['title'],
                "province" => $hit['_source']['location_primary'],
                "district" => $hit['_source']['location_secondary'],
                "salary_min" => $hit['_source']['salary_min'],
                "salary_max" => $hit['_source']['salary_max'],
                "sector" => $sectorsHashTable[$hit['_source']['sectorID']] ?? null,
                "date_processed" => $hit['_source']['date_processed'],
                "deadline" => $hit['_source']['deadline']
            ];
        }, $response['hits']['hits']);

        return json_encode($documents);
    }

    public function getSectors() {
        $params_sectors = [
            'index' => 'sector',
            'body' => [
                'query' => [
                    'match_all' => new \stdClass() 
                ],
                '_source' => ["sectorID", "name"],  
                'size' => 20  
            ]
        ];
        $sectors = $this->elasticService->client->search($params_sectors)['hits']['hits'];
        
        $sectorsHashTable = array_reduce($sectors, function ($carry, $hit) {
            $carry[$hit['_source']['sectorID']] = $hit['_source']['name'];
            return $carry;
        }, []);

        return $sectorsHashTable;
    }
}