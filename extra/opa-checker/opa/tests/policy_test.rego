package federated.enrollment_test

import data.federated.enrollment
import future.keywords.if

test_valid_enrollment if {
    result := enrollment.allow with input as {
        "client": {
            "id": "test_client_1",
            "certificate_valid": true,
            "identity": "client@example.com",
            "dataset_size": 500,
            "cpu_cores": 4,
            "memory_gb": 8
        }
    } with data as {
        "enrollment": {
            "min_dataset_size": 100,
            "min_cpu_cores": 2,
            "min_memory_gb": 4,
            "start_time": 0,
            "end_time": 9999999999999999999
        },
        "blacklist": {
            "client_ids": []
        }
    }

    result == true
}

test_blacklisted_client if {
    result := enrollment.allow with input as {
        "client": {
            "id": "bad_client",
            "certificate_valid": true,
            "identity": "bad@example.com",
            "dataset_size": 500,
            "cpu_cores": 4,
            "memory_gb": 8
        }
    } with data as {
        "enrollment": {
            "min_dataset_size": 100,
            "min_cpu_cores": 2,
            "min_memory_gb": 4,
            "start_time": 0,
            "end_time": 9999999999999999999
        },
        "blacklist": {
            "client_ids": ["bad_client"]
        }
    }

    result == false
}