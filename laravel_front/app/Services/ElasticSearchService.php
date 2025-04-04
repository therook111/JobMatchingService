<?php

namespace App\Services;

use Elastic\Elasticsearch\ClientBuilder;
use Illuminate\Support\Facades\Http;

class ElasticSearchService 
{
    private $baseUrl;
    private $elastic_username;
    private $elastic_password;

    function __construct() {
        $this->baseUrl = env('ELASTICSEARCH_HOST', 'http://localhost:9200');
        $this->elastic_username = env('ELASTICSEARCH_USERNAME', 'elastic');
        $this->elastic_password = env('ELASTICSEARCH_PASSWORD', 'password');

        $this->client = ClientBuilder::create()
            ->setHosts([$this->baseUrl])
            ->setBasicAuthentication($this->elastic_username, $this->elastic_password)
            ->build();
    }
}