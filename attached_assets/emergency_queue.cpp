#include <iostream>
#include <queue>
#include <vector>
#include <string>
#include <ctime>
#include <cstring>
#include <fstream>
#include <sstream>

// Emergency case structure
struct EmergencyCase {
    std::string patient_id;
    std::string name;
    int priority_level;
    std::string condition;
    std::time_t timestamp;

    EmergencyCase(std::string pid, std::string n, int pri, std::string cond)
        : patient_id(pid), name(n), priority_level(pri), condition(cond) {
        timestamp = std::time(nullptr);
    }
};

// Comparator for priority queue
struct CompareCases {
    bool operator()(const EmergencyCase& a, const EmergencyCase& b) {
        return a.priority_level > b.priority_level; // lower value = higher priority
    }
};

std::priority_queue<EmergencyCase, std::vector<EmergencyCase>, CompareCases> emergency_queue;

// Convert priority string to int
int convert_priority_level(const std::string& priority) {
    if (priority == "Emergency") return 1;
    if (priority == "Urgent") return 2;
    if (priority == "Standard") return 3;
    if (priority == "Routine") return 4;
    return 4;
}

extern "C" {

// Add a case to the queue
bool add_emergency_case(const char* patient_id, const char* name, const char* priority, const char* condition) {
    try {
        int pri_level = convert_priority_level(priority);
        EmergencyCase new_case(patient_id, name, pri_level, condition);
        emergency_queue.push(new_case);

        std::ofstream log_file("data/emergency_log.csv", std::ios::app);
        if (!log_file.is_open()) {
            std::ofstream new_file("data/emergency_log.csv");
            if (new_file.is_open()) {
                new_file << "patient_id,name,priority_level,condition,timestamp\n";
                new_file.close();
                log_file.open("data/emergency_log.csv", std::ios::app);
            }
        }

        if (log_file.is_open()) {
            log_file << new_case.patient_id << ","
                     << new_case.name << ","
                     << pri_level << ","
                     << new_case.condition << ","
                     << new_case.timestamp << std::endl;
            log_file.close();
        }

        return true;
    } catch (...) {
        return false;
    }
}

// Get the next emergency case from the queue
bool get_next_emergency_case(char* patient_id, char* name, int* priority, char* condition, time_t* timestamp) {
    if (emergency_queue.empty()) {
        return false;
    }

    EmergencyCase next_case = emergency_queue.top();
    emergency_queue.pop();

    std::strcpy(patient_id, next_case.patient_id.c_str());
    std::strcpy(name, next_case.name.c_str());
    *priority = next_case.priority_level;
    std::strcpy(condition, next_case.condition.c_str());
    *timestamp = next_case.timestamp;

    return true;
}

// Get queue size
int get_emergency_queue_size() {
    return emergency_queue.size();
}

// Load from CSV
int load_emergency_cases_from_csv() {
    std::ifstream file("data/emergency_log.csv");
    if (!file.is_open()) return 0;

    std::string line;
    std::getline(file, line); // skip header

    int count = 0;
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string pid, name, pri_str, cond, time_str;

        std::getline(ss, pid, ',');
        std::getline(ss, name, ',');
        std::getline(ss, pri_str, ',');
        std::getline(ss, cond, ',');
        std::getline(ss, time_str, ',');

        int priority = std::stoi(pri_str);
        std::time_t ts = std::stol(time_str);

        EmergencyCase ec(pid, name, priority, cond);
        ec.timestamp = ts;
        emergency_queue.push(ec);
        ++count;
    }

    file.close();
    return count;
}

// Clear queue
void clear_emergency_queue() {
    while (!emergency_queue.empty()) {
        emergency_queue.pop();
    }
}

// Get all cases in JSON format
void get_all_emergency_cases(char* output, int max_size) {
    auto temp_queue = emergency_queue;
    std::string result = "[";

    bool first = true;
    while (!temp_queue.empty()) {
        EmergencyCase ec = temp_queue.top();
        temp_queue.pop();

        if (!first) result += ",";
        first = false;

        result += "{\"patient_id\":\"" + ec.patient_id + "\",";
        result += "\"name\":\"" + ec.name + "\",";
        result += "\"priority_level\":" + std::to_string(ec.priority_level) + ",";
        result += "\"condition\":\"" + ec.condition + "\",";
        result += "\"timestamp\":" + std::to_string(ec.timestamp) + "}";
    }

    result += "]";
    std::strncpy(output, result.c_str(), max_size - 1);
    output[max_size - 1] = '\0';
}

// Convert priority number to string
void get_priority_name(int priority, char* output, int max_size) {
    std::string pname = "Unknown";
    switch (priority) {
        case 1: pname = "Emergency"; break;
        case 2: pname = "Urgent"; break;
        case 3: pname = "Standard"; break;
        case 4: pname = "Routine"; break;
    }

    std::strncpy(output, pname.c_str(), max_size - 1);
    output[max_size - 1] = '\0';
}

} // extern "C"
