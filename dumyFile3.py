def find_port_number(data):
  # Check if the data contains only 0s and 1s
  if not all(bit in ['0', '1'] for bit in data):
    return "Invalid data format"

  # Check for the special cases where we should skip
  if data.count('1') != 1 or data.count('0') == len(data) or data.count('0') == 0:
    return "Skip"

  # Find the index of '1' in the data
  port_number = data.index('1') + 1
  return port_number
if __name__ == '__main__':

# Example data
 data1 = "0010000000"
 data2 = "0100000000"
 data3 = "1111111101"
 data4 = "0000000000"

# Testing the function with example data
 print(find_port_number(data1))  # Output: 3
 print(find_port_number(data2))  # Output: 1
 print(find_port_number(data3))  # Output: Skip
 print(find_port_number(data4))  # Output: Skip

