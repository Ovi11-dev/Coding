/*

[ASSIGNMENT]: Transform To Prime

TASK: Given a list[ ] of n integers, find minimum number to be inserted in a list, so that sum of all elements
of list should equal the closest prime number.

NOTE!
- List size is at least 2.
- List's numbers will only positives (n > 0).
- Repeatition of numbers in numbers in the list could
  occur.
- The newer list's sum should equal the
  closest prime number.

Example #1

minimumNumber({3, 1, 2}) --> return (1)

Explanation:
Since, the sum of the list's elements equal to (6), the minimum number to be inserted to transform the sum
to prime number is (1), which will make the sum of the List equal the closest prime number (7).

Example #2

minimumNumber({2, 12, 8, 4, 6}) --> return (5)

Explanation:
Since, the sum of the list's elements equal to (32), the minimum number to be inserted to transform the
sum to prime number is (5), which will make the sum of the List equal the closest prime number (37).

#HappyCodings! :)
Enter your numbers seperated by spaces.

*/

func prime(x:Int) -> Bool {
    var b = true
    if(x < 2) {
        b = false
    } else if(x == 2) {
        b = true
    } else {
        for i in 2 ... x - 1 {
            if(x % i == 0 && x != 2) {
                b = false
                break
            }
        }
    }
    
    return b
}

var n = readLine()!.split(seperator: " ").map({ Int($0)! })

var sum = n.reduce(0, { z, y in z + y })

var count = 0

while(true) {
    if(prime(x:sum)) {
        break
    }
    
    sum += 1
    count += 1
}

print("You entered \(n) and you have to add \(count) to make it a prime number.")
