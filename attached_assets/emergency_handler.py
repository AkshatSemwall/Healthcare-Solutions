"""
Emergency Handler Module - Python interface to the C++ emergency queue implementation
"""
import os
import ctypes
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Define the path to the shared library
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libemergency.so')

# Try to load the library
try:
    emergency_lib = ctypes.CDLL(lib_path)
    logger.info(f"Successfully loaded emergency handling library from {lib_path}")
except Exception as e:
    logger.error(f"Failed to load emergency handling library: {str(e)}")
    emergency_lib = None

class EmergencyHandler:
    """Python wrapper for the C++ emergency queue implementation"""
    
    def __init__(self):
        """Initialize the emergency handler"""
        if emergency_lib is None:
            logger.error("Emergency handling library not loaded. Functionality will be limited.")
            return
        
        # Define the function prototypes
        self._add_emergency_case = emergency_lib.add_emergency_case
        self._add_emergency_case.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self._add_emergency_case.restype = ctypes.c_bool
        
        self._get_next_emergency_case = emergency_lib.get_next_emergency_case
        self._get_next_emergency_case.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int),
            ctypes.c_char_p, ctypes.POINTER(ctypes.c_long)
        ]
        self._get_next_emergency_case.restype = ctypes.c_bool
        
        self._get_emergency_queue_size = emergency_lib.get_emergency_queue_size
        self._get_emergency_queue_size.argtypes = []
        self._get_emergency_queue_size.restype = ctypes.c_int
        
        self._load_emergency_cases_from_csv = emergency_lib.load_emergency_cases_from_csv
        self._load_emergency_cases_from_csv.argtypes = []
        self._load_emergency_cases_from_csv.restype = ctypes.c_int
        
        self._clear_emergency_queue = emergency_lib.clear_emergency_queue
        self._clear_emergency_queue.argtypes = []
        self._clear_emergency_queue.restype = None
        
        self._get_all_emergency_cases = emergency_lib.get_all_emergency_cases
        self._get_all_emergency_cases.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self._get_all_emergency_cases.restype = None
        
        self._get_priority_name = emergency_lib.get_priority_name
        self._get_priority_name.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        self._get_priority_name.restype = None
        
        # Load any existing emergency cases
        self.load_cases_from_csv()
        
    def add_case(self, patient_id, name, priority, condition):
        """
        Add a new emergency case to the queue
        
        Args:
            patient_id (str): Patient ID
            name (str): Patient name
            priority (str): Priority level (Emergency, Urgent, Standard, Routine)
            condition (str): Medical condition
            
        Returns:
            bool: True if successful, False otherwise
        """
        if emergency_lib is None:
            logger.error("Emergency handling library not loaded. Cannot add case.")
            return False
        
        try:
            result = self._add_emergency_case(
                ctypes.c_char_p(patient_id.encode('utf-8')),
                ctypes.c_char_p(name.encode('utf-8')),
                ctypes.c_char_p(priority.encode('utf-8')),
                ctypes.c_char_p(condition.encode('utf-8'))
            )
            
            if result:
                logger.info(f"Added emergency case for patient {patient_id} with priority {priority}")
            else:
                logger.error(f"Failed to add emergency case for patient {patient_id}")
                
            return result
        except Exception as e:
            logger.error(f"Error adding emergency case: {str(e)}")
            return False
    
    def get_next_case(self):
        """
        Get the next highest priority case from the queue
        
        Returns:
            dict: Case information or None if queue is empty
        """
        if emergency_lib is None:
            logger.error("Emergency handling library not loaded. Cannot get next case.")
            return None
        
        try:
            # Create buffers for the output
            patient_id_buffer = ctypes.create_string_buffer(100)
            name_buffer = ctypes.create_string_buffer(256)
            priority = ctypes.c_int()
            condition_buffer = ctypes.create_string_buffer(1024)
            timestamp = ctypes.c_long()
            
            result = self._get_next_emergency_case(
                patient_id_buffer, name_buffer, ctypes.byref(priority),
                condition_buffer, ctypes.byref(timestamp)
            )
            
            if result:
                # Get the priority level name
                priority_name_buffer = ctypes.create_string_buffer(50)
                self._get_priority_name(priority.value, priority_name_buffer, 50)
                
                # Format timestamp
                dt = datetime.fromtimestamp(timestamp.value)
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                
                case = {
                    'patient_id': patient_id_buffer.value.decode('utf-8'),
                    'name': name_buffer.value.decode('utf-8'),
                    'priority_level': priority.value,
                    'priority_name': priority_name_buffer.value.decode('utf-8'),
                    'condition': condition_buffer.value.decode('utf-8'),
                    'timestamp': timestamp.value,
                    'formatted_time': formatted_time
                }
                
                logger.info(f"Retrieved next emergency case: {case['patient_id']}")
                return case
            else:
                logger.info("No emergency cases in the queue")
                return None
        except Exception as e:
            logger.error(f"Error getting next emergency case: {str(e)}")
            return None
    
    def get_queue_size(self):
        """
        Get the current size of the emergency queue
        
        Returns:
            int: Number of cases in the queue
        """
        if emergency_lib is None:
            logger.error("Emergency handling library not loaded. Cannot get queue size.")
            return 0
        
        try:
            size = self._get_emergency_queue_size()
            logger.debug(f"Emergency queue contains {size} cases")
            return size
        except Exception as e:
            logger.error(f"Error getting emergency queue size: {str(e)}")
            return 0
    
    def load_cases_from_csv(self):
        """
        Load emergency cases from CSV file
        
        Returns:
            int: Number of cases loaded
        """
        if emergency_lib is None:
            logger.error("Emergency handling library not loaded. Cannot load cases.")
            return 0
        
        try:
            count = self._load_emergency_cases_from_csv()
            logger.info(f"Loaded {count} emergency cases from CSV")
            return count
        except Exception as e:
            logger.error(f"Error loading emergency cases from CSV: {str(e)}")
            return 0
    
    def clear_queue(self):
        """Clear all cases from the emergency queue"""
        if emergency_lib is None:
            logger.error("Emergency handling library not loaded. Cannot clear queue.")
            return
        
        try:
            self._clear_emergency_queue()
            logger.info("Cleared emergency queue")
        except Exception as e:
            logger.error(f"Error clearing emergency queue: {str(e)}")
    
    def get_all_cases(self):
        """
        Get all cases currently in the emergency queue
        
        Returns:
            list: List of cases
        """
        if emergency_lib is None:
            logger.error("Emergency handling library not loaded. Cannot get cases.")
            return []
        
        try:
            # Create a buffer for the JSON output
            buffer_size = 100000  # Adjust as needed
            output_buffer = ctypes.create_string_buffer(buffer_size)
            
            self._get_all_emergency_cases(output_buffer, buffer_size)
            
            # Parse the JSON string
            json_str = output_buffer.value.decode('utf-8')
            cases = json.loads(json_str)
            
            # Format the cases
            formatted_cases = []
            for case in cases:
                # Get the priority level name
                priority_name_buffer = ctypes.create_string_buffer(50)
                self._get_priority_name(case['priority_level'], priority_name_buffer, 50)
                
                # Format timestamp
                dt = datetime.fromtimestamp(case['timestamp'])
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                
                formatted_case = {
                    'patient_id': case['patient_id'],
                    'name': case['name'],
                    'priority_level': case['priority_level'],
                    'priority_name': priority_name_buffer.value.decode('utf-8'),
                    'condition': case['condition'],
                    'timestamp': case['timestamp'],
                    'formatted_time': formatted_time
                }
                
                formatted_cases.append(formatted_case)
            
            logger.debug(f"Retrieved {len(formatted_cases)} emergency cases")
            return formatted_cases
        except Exception as e:
            logger.error(f"Error getting all emergency cases: {str(e)}")
            return []


# Create a singleton instance
emergency_handler = EmergencyHandler()