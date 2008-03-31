/*

Points class.
-Keeps track of the player's points throughout an exchange oppertunity
-Calculates points preview during offer formulation

*/

function et_points(){
	this.p1x;
	this.p2x;
	this.p1y;
	this.p2y;
	
	this.p1xValue_raw;
	this.p2xValue_raw;
	this.p1yValue_raw;
	this.p2yValue_raw;

	this.p1xValue;
	this.p2xValue;
	this.p1yValue;
	this.p2yValue;	
	
	this.offer;
	this.offerUnit;
	this.request;
	this.requestUnit;
	
	this.offeredBy;
	
	this.p1xMaxRequest;
	this.p2xMaxRequest;
	this.p1yMaxRequest;
	this.p2yMaxRequest;

	this.lastResponse;

	this.calculatePoints = function(){	  
		// todo: Make sure all the variables we're going to use are present. 
		if(!this.verifyObjectVariables()){
			console.log("Error: verifyObjectVariables failed");
			console.dir(this);
			return false;
		} else {
			
			// Initialize a response object to return
			response = {'error': false};
			
			// Check if the player has offered more than they have
			if(parseInt(this.offer) > parseInt(eval('this.'+this.offeredBy+this.offerUnit))) {
				response.error = true;
				response.errorMsg = "Insufficient funds for offer";
				return response;
			}
			if(parseInt(this.request) > parseInt(eval('this.'+this.offeredBy+this.requestUnit+'MaxRequest'))) {
				response.error = true;
				response.errorMsg = "Exceeded max request";
				return response;
			}
			
			// Parse the raw values
			this.p1xValue = this.parseValue(this.p1xValue_raw);
			this.p2xValue = this.parseValue(this.p2xValue_raw);		
			this.p1yValue = this.parseValue(this.p1yValue_raw);		
			this.p2yValue = this.parseValue(this.p2yValue_raw);
			
			// Calculate the initial number of points held by the player at the start of the transaction
			p1InitialPoints = (this.p1x * this.p1xValue) + (this.p1y * this.p1yValue);
			p2InitialPoints = (this.p2x * this.p2xValue) + (this.p2y * this.p2yValue);

			// Calculate the Gain and Loss for each player
			if(this.offeredBy == "p1"){
				p1Gain = this.request * eval('this.p1'+this.requestUnit.toLowerCase()+'Value');
				p2Gain = this.offer * eval('this.p2'+this.offerUnit.toLowerCase()+'Value');
				p1Loss = this.offer * eval('this.p1'+this.offerUnit.toLowerCase()+'Value');
				p2Loss = this.request * eval('this.p2'+this.requestUnit.toLowerCase()+'Value');
			} else if(this.offeredBy == "p2") {
				p1Gain = this.offer * eval('this.p1'+this.offerUnit.toLowerCase()+'Value');
				p2Gain = this.request * eval('this.p2'+this.requestUnit.toLowerCase()+'Value');
				p1Loss = this.request * eval('this.p1'+this.requestUnit.toLowerCase()+'Value');
				p2Loss = this.offer * eval('this.p2'+this.offerUnit.toLowerCase()+'Value');
			}
			
      

			// calculate the potential points
			p1Points = p1InitialPoints + (p1Gain - p1Loss);
			p2Points = p2InitialPoints + (p2Gain - p2Loss);		

			p1Points_justExchange = p1Gain - p1Loss;
			p2Points_justExchange = p2Gain - p2Loss;
			
			response.p1InitialPoints = p1InitialPoints;
			response.p2InitialPoints = p2InitialPoints;
			response.p1Points = p1Points;
			response.p2Points = p2Points;
			response.p1Points_justExchange = p1Points_justExchange;
			response.p2Points_justExchange = p2Points_justExchange;
			
			this.lastResponse = response;
			
			return response;
		}
	}
	
	this.parseValue = function(rawValue){
		
		//Check if input is just digits, if so return value input right away
		if(/^\d+$/.test(rawValue)){
			return rawValue;
		}
		//replace variables if present
		if(this.offerUnit == "x"){
			rawValue = rawValue.replace(/Ox/g, this.offer);
			rawValue = rawValue.replace(/Oy/g, "0");
		} else {
			rawValue = rawValue.replace(/Ox/g, "0");
			rawValue = rawValue.replace(/Oy/g, this.offer);
		}
		if(this.requestUnit == "x"){
			rawValue = rawValue.replace(/Rx/g, this.request);
			rawValue = rawValue.replace(/Ry/g, "0");
		} else {
			rawValue = rawValue.replace(/Rx/g, "0");
			rawValue = rawValue.replace(/Ry/g, this.request);
		}
		if(this.offeredBy == "p1"){
			rawValue = rawValue.replace(/Axo/g, this.p1x);
			rawValue = rawValue.replace(/Ayo/g, this.p1y);
			rawValue = rawValue.replace(/Axr/g, this.p2x);
			rawValue = rawValue.replace(/Ayr/g, this.p2y);
		} else {
			rawValue = rawValue.replace(/Axo/g, this.p2x);
			rawValue = rawValue.replace(/Ayo/g, this.p2y);
			rawValue = rawValue.replace(/Axr/g, this.p1x);
			rawValue = rawValue.replace(/Ayr/g, this.p1y);
		}

		//evaluate value expression and return it
		try{
			processedValue = eval(rawValue);
			processedValue = Math.round(processedValue);
		} catch(err){
			msg = "There is an error in one of your value fields!\n\n";
			msg += "Error: Syntax Error";
			alert(msg);
			processedValue = false;
		}
		
		return processedValue;
	}
	
	this.verifyObjectVariables = function(){
		valid = true;
		
		// This handles the case where either offer or request is left blank
		if(this.offer == ""){this.offer = "0";}
		if(this.request == ""){this.request = "0";}
		
		// All of these properties should have values
		[	this.p1x,
			this.p2x,
			this.p1y,
			this.p2y,
			this.p1xValue_raw,
			this.p2xValue_raw,
			this.p1yValue_raw,
			this.p2yValue_raw,
			this.offer,
			this.offerUnit,
			this.request,
			this.requestUnit,
			this.offeredBy,
			this.p1xMaxRequest,
			this.p2xMaxRequest,
			this.p1yMaxRequest,
			this.p2yMaxRequest
		].forEach(function(element, index, array){
			if(element == null || element == "" || element < 0){
				valid = false;
			}
		});
		
		return valid;
		
	}
}
