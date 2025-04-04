@extends('layouts.app')

@section('content')
    <style>
        h1 {
            text-align: center;
            font-family: 'Nunito', sans-serif;
            font-size: 24px;
            color: #008080;
        }

        .dataframe {
          border-collapse: collapse;
          margin: 25px 0;
          font-size: 0.9em;
          font-family: 'Nunito', sans-serif;
          min-width: 400px;
          box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
          width: 80%;
          margin: 0 auto;
        }

        .dataframe thead tr {
            background-color: #009879;
            color: #ffffff;
            text-align: left;
        }

        .dataframe th, .dataframe td {
            padding: 12px 15px;
        }

        .dataframe tbody tr {
            border-bottom: 1px solid #dddddd;
        }

        .dataframe tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }

        .dataframe tbody tr:last-of-type {
            border-bottom: 2px solid #009879;
        }

        form {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            max-width: 80%;
            margin: 0 auto 50px;
            padding: 20px;
            background-color: #ffffff;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .form-group {
            flex: 1 1 200px;
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: bold;
            margin-bottom: 5px;
            font-family: 'Nunito', sans-serif;
        }
        input, select {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            width: 100%;
            box-sizing: border-box;
            font-family: 'Nunito', sans-serif;
        }
        .form-actions {
            flex: 1 1 100%;
            text-align: center;
            font-family: 'Nunito', sans-serif;
        }
        button {
            padding: 10px 20px;
            background-color: #009879;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-family: 'Nunito', sans-serif;
        }
        button:hover {
            background-color: #007f65;
        }
        .salary-range {
            display: flex;
            gap: 10px;
        }
        .salary-range input {
            flex: 1;
        }
    </style>

    <h1 class="text-center">Our top 20 recommended jobs for you</h1>

    <form id="filtersForm" method="POST" action="{{ route('filter.jobs') }}">
        @csrf
        <div id="cvid"></div>

        <div class="form-group">
            <label for="province">Province</label>
            <select id="province" name="province">
                <option value="">Select a province</option>
            </select>
        </div>

        <div class="form-group">
            <label for="district">District</label>
            <select id="district" name="district">
                <option value="">Select a district</option>
            </select>
        </div>

        <div class="form-group">
            <label for="filter_salary_mode">Salary Filter Mode</label>
            <select id="filter_salary_mode" name="filter_salary_mode">
                <option value="">None</option>
                <option value="max">Maximum of</option>
                <option value="min">Minimum of</option>
                <option value="range">Range</option>
            </select>
        </div>

        <div class="form-group" id="salary-container">
            <label for="salary">Salary Threshold</label>
            <input type="number" id="salary" name="salary" placeholder="Enter salary threshold">
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Submit</button>
        </div>
    </form>

    <div id="resultContainer">
        @isset($results)
            {!! $results !!} <!-- Render results directly -->
        @endisset
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function () {
            const provinceSelect = document.getElementById("province");
            const districtSelect = document.getElementById("district");
            const salaryFilterMode = document.getElementById("filter_salary_mode");
            const salaryContainer = document.getElementById("salary-container");

            async function fetchProvinces() {
                try {
                    const response = await fetch("{{ route('api.provinces') }}");
                    return response.ok ? await response.json() : [];
                } catch (error) {
                    console.error("Error fetching provinces:", error);
                    return [];
                }
            }

            async function fetchDistricts(provinceCode) {
                try {
                    const response = await fetch(`{{ url('/api/districts') }}/${provinceCode}`);
                    return response.ok ? await response.json() : [];
                } catch (error) {
                    console.error("Error fetching districts:", error);
                    return [];
                }
            }

            async function initializeProvinces() {
                provinceSelect.innerHTML = '<option value="">Loading provinces...</option>';
                provinceSelect.disabled = true;
                
                const provinces = await fetchProvinces();
                
                provinceSelect.innerHTML = '<option value="">Select a province</option>';
                provinces.forEach(province => {
                    let option = new Option(province.name, province.code);
                    provinceSelect.appendChild(option);
                });
                
                provinceSelect.disabled = false;
            }

            provinceSelect.addEventListener("change", async () => {
                const selectedProvince = provinceSelect.value;
                
                if (selectedProvince) {
                    districtSelect.innerHTML = '<option value="">Loading districts...</option>';
                    districtSelect.disabled = true;
                    
                    const districts = await fetchDistricts(selectedProvince);
                    districtSelect.disabled = false;
                    
                    districtSelect.innerHTML = '<option value="">Select a district</option>';
                    districts.forEach(district => {
                        let option = new Option(district.name, district.code);
                        districtSelect.appendChild(option);
                    });
                } else {
                    districtSelect.innerHTML = '<option value="">Select a district</option>';
                    districtSelect.disabled = true;
                }
            });

            salaryFilterMode.addEventListener("change", () => {
                if (salaryFilterMode.value === "range") {
                    salaryContainer.innerHTML = `
                        <label>Salary Range</label>
                        <div class="salary-range">
                            <input type="number" name="salary_min" placeholder="Minimum" required>
                            <input type="number" name="salary_max" placeholder="Maximum" required>
                        </div>
                    `;
                } else if (salaryFilterMode.value === "") {
                    salaryContainer.innerHTML = "";
                } else {
                    salaryContainer.innerHTML = `
                        <label for="salary">Salary Threshold</label>
                        <input type="number" name="salary" placeholder="Enter salary threshold" required>
                    `;
                }
            });

            initializeProvinces();
        });
    </script>
@endsection