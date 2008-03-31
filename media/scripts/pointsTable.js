/** This is how you write javascript
 *
 * This is a simple javascript object which calculates the points for
 * display on the NEX offer page.  It uses a lookup table.
 * @author n8agrin
 *
 */
(function(){  // WRAP YOUR LOCAL ENVIRONMENT SO THAT YOU DON'T COLLIDE WITH
              // EVERYONE AND THING

// PointsTable object that stores the point table and has a simple method for
// looking up the transaction total based on a given amount of X and Y offered
// or received.    

// This is a singleton!  Surprise!
var PointsTable = window.PointsTable = new function() {
  
  // The tables used by the PointsTable object are private.
  // You can't access them, change them, mutate them, modify them,
  // reset them, paint them, throw them out, you can't even iterate
  // over them.
  
  // table is indexed by the amount of Y received.
  // this confuses me but it's the way I was handed the data.
  // so, for example, I was given this data:
  // GIVE X	|| RECEIVE Y	|| OFFER TOTALS FOR P1	|| OFFER TOTALS FOR P2
  // 10	        1	          -19	                      80
  // 9	        1	          -18	                      79
  // 8	        1	          -17	                      78
  // 7	        1	          -16	                      77
  // 6	        1	          -15	                      76
  //
  // so the table is build like:
  // [
  //  [[10, 51], [9, 52], [8, 53], [], [], [], [], [], [], []]
  //  [],
  //  []
  // ]
  // in this way you look up the y points received first:
  // table[1][2] would be equal to 1 y point received and 2 x points given
  var xytable = [
    // give 1x
    [[10,51], [15,46], [20,41], [25,36], [30,31], [60,1], [65,-4], [70,-9], [75,-14], [80,-19]],
    // give 2x
    [[9,52], [14,47], [19,42], [24,37], [29,32], [59,2], [64,-3], [69,-8], [74,-13], [79,-18]],
    // give 3x
    [[8,53], [13,48], [18,43], [23,38], [28,33], [58,3], [63,-2], [68,-7], [73,-12], [78,-17]],
    // give 4x
    [[7,54], [12,49], [17,44], [22,39], [27,34], [57,4], [62,-1], [67,-6], [72,-11], [77,-16]],
    // give 5x
    [[6,55], [11,50], [16,45], [21,40], [26,35], [56,5], [61,0], [66,-5], [71,-10], [76,-15]],
    // give 6x
    [[-15,76], [-10,71], [-5,66], [0, 61], [5,56], [35,26], [40,21], [45,16], [50,11], [55,6]],
    // give 7x
    [[-16,77], [-11,72], [-6,67], [-1,62], [4,57], [34,27], [39,22], [44,17], [49,12], [54,7]],
    // give 8x
    [[-17,78], [-12,73], [-7,68], [-2,63], [3,58], [33,28], [38,23], [43,18], [48,13], [53,8]],
    // give 9x
    [[-18,79], [-13,74], [-8,69], [-3,64], [2,59], [32,29], [37,24], [42,19], [47,14], [52,9]],
    // give 10x
    [[-19,80], [-14,75], [-9,70], [-4,65], [1,60], [31,30], [36,25], [41,20], [46,15], [51,10]]
  ];

  // Give 1 x and receive 4 x = [-2,4]
  // and is equivelant to:
  // yytable[1][4];
  // the returned [-2,4] are the points given to p1 and p2 respectively
  var xxtable = [
    [[1,1], [0,2], [-1,3], [-2,4], [-3,5], [-4,6], [-5,7], [-6,8], [-7.9], [-8,10]]
  ];
  
  // Give 1 Y and receive 4 y = [4,-2]
  // and is equivelant to:
  // yytable[0][3];
  // the returned [4,-2] are the points given to p1 and p2 respectively
  var yytable = [
    [[1,1], [2,0], [3,-1], [4,-2], [5,-3], [6,-4], [7,-5], [8,-6], [9,-7], [10,-8]]
  ];

  // Look up a point return value based on the types of points exchanged
  // and the amount of the points exchanged.
  // Does so in a safe way, that is, safe both for the accessed point
  // table array, safe for the rest of the javascript environment this
  // script will be included in and safe for the lifetime of this entire
  // project.  Hurray!
  this.findTotal = function(giveType, receiveType, give, receive) {
    
    // Notice how I use VAR on everything?  Huh, notice that?  It's nice
    // right, because it doesn't destroy or reset other real global
    // variables.
    var giveIndex = give - 1;
    var receiveIndex = receive -1;
    var table; // holds the chosen table
    
    if (giveType == 'x' && receiveType == 'x') {
      table = xxtable;
    }
    else if (giveType == 'y' && receiveType == 'y') {
      table = yytable;
    }
    else {
      table = xytable;
    }
    
    if ((giveIndex < 0 || giveIndex > table.length - 1) ||
        (receiveIndex < 0 || receiveIndex > table[giveIndex].length - 1)){
      return false;
    } 
    return table[giveIndex][receiveIndex];
  }
}

})();