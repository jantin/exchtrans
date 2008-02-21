var undef;var internalRules;function performCheck(H,l,J){var p=makeRules(l);internalRules=makeRules(l);this.f=document.forms[H];if(!this.f){debug("DEBUG: could not find form object "+H);return null;}var B=new Array();var C=0;if(p.length){for(var w=0;w<p.length;w++){var L=p[w];if(L!=null){highlight(getField(f,L.el),inputclassnormal);}}}else{if(p!=null){highlight(getField(f,p.el),inputclassnormal);}}if(p.length){for(var w=0;w<p.length;w++){var L=p[w];var A=null;if(L==null){}else{if(L.ruleType=="pre-condition"||L.ruleType=="post-condition"){}else{if(L.ruleName=="implies"){pre=L.el;post=L.comparisonValue;var R=getField(f,p[pre].el).className;if(checkRule(f,p[pre])==null&&checkRule(f,p[post])!=null){A=L.alertMsg;}else{if(checkRule(f,p[pre])!=null){getField(f,p[pre].el).className=R;}}}else{A=checkRule(f,L);}}}if(A!=null){B[C]=A;C++;}}}else{var e=p;err=checkRule(f,e);if(err!=null){B[0]=err;}}return displayAlert(B,J);}function checkKeyPress(w,B,R){var L=null;if(getBrowser()=="msie"){L=window.event.keyCode;}else{if(getBrowser()=="netscape"||getBrowser()=="firefox"){L=w.which;}}var l=makeRules(R);var A=true;if(l.length){for(var J=0;J<l.length;J++){var C=l[J];if(C.ruleName=="keypress"&&C.el==B.name){A=isKeyAllowed(L,C.comparisonValue);break;}}}else{var C=l;if(C.ruleName=="keypress"&&C.el==B.name){A=isKeyAllowed(L,C.comparisonValue);}}if(!A){if(getBrowser()=="msie"){window.event.keyCode=0;}else{if(getBrowser()=="netscape"||getBrowser()=="firefox"){w.preventDefault();w.stopPropagation();w.returnValue=false;}}}return false;}function displayAlert(C,A){var R=null;if(A=="classic"){R=displayClassic(C);}else{if(A=="innerHtml"){R=displayInnerHtml(C);}else{if(A=="jsVar"){R=displayJsVar(C);}else{debug("DEBUG: alert type "+A+" not supported");}}}return R;}function displayClassic(A){var C="";if(A!=null&&A.length>0){if(strTrim(HEADER_MSG).length>0){C+=HEADER_MSG+"\n\n";}for(var R=0;R<A.length;R++){C+=" "+A[R]+"\n";}if(strTrim(FOOTER_MSG).length>0){C+="\n"+FOOTER_MSG;}alert(C);return false;}else{return true;}}function displayInnerHtml(A){if(A!=null&&A.length>0){var C="";if(strTrim(HEADER_MSG).length>0){C+=HEADER_MSG;}C+="<ul>";for(var R=0;R<A.length;R++){C+="<li>"+A[R]+"</li>";}C+="</ul>";if(strTrim(FOOTER_MSG).length>0){C+=FOOTER_MSG;}document.getElementById(errorsdiv).innerHTML=C;document.getElementById(errorsdiv).className=innererror;document.getElementById(errorsdiv).style.display="block";return false;}else{document.getElementById(errorsdiv).innerHTML="";document.getElementById(errorsdiv).className="";document.getElementById(errorsdiv).style.display="none";return true;}}function displayJsVar(R){document.getElementById(errorsdiv).className="";document.getElementById(errorsdiv).style.display="none";if(R!=null&&R.length>0){var A="";A+="<script>var jsErrors;</script>";document.getElementById(errorsdiv).innerHTML=A;jsErrors=R;return false;}else{document.getElementById(errorsdiv).innerHTML="<script>var jsErrors;</script>";return true;}}function rule(A,J,C,R,w){if(!checkArguments(arguments)){return false;}tmp=A.split(":");nameDisplayed="";if(tmp.length==2){nameDisplayed=tmp[1];A=tmp[0];}this.el=A;this.nameDisplayed=nameDisplayed;this.ruleName=J;this.comparisonValue=C;this.ruleType=w;if(R==undef||R==null){this.alertMsg=getDefaultMessage(A,nameDisplayed,J,C);}else{this.alertMsg=R;}}function checkRule(f,myRule){retVal=null;if(myRule!=null){if(myRule.ruleName=="custom"){var customFunction=" retVal = "+myRule.el;eval(customFunction);}else{if(myRule.ruleName=="and"){var op_1=myRule.el;var op_next=myRule.comparisonValue;if(checkRule(f,internalRules[op_1])!=null){retVal=myRule.alertMsg;if(myRule.ruleType=="pre-condition"){highlight(getField(f,internalRules[op_1].el),inputclassnormal);}}else{var op_k=op_next.split("-");for(var k=0;k<op_k.length;k++){if(checkRule(f,internalRules[op_k[k]])!=null){retVal=myRule.alertMsg;if(myRule.ruleType=="pre-condition"){highlight(getField(f,internalRules[op_k[k]].el),inputclassnormal);}break;}}}}else{if(myRule.ruleName=="or"){var op_1=myRule.el;var op_next=myRule.comparisonValue;var success=false;if(checkRule(f,internalRules[op_1])==null){success=true;}else{if(myRule.ruleType=="pre-condition"){highlight(getField(f,internalRules[op_1].el),inputclassnormal);}var op_k=op_next.split("-");for(var k=0;k<op_k.length;k++){if(checkRule(f,internalRules[op_k[k]])==null){success=true;break;}else{if(myRule.ruleType=="pre-condition"){highlight(getField(f,internalRules[op_k[k]].el),inputclassnormal);}}}}if(!success){retVal=myRule.alertMsg;}}else{el=getField(f,myRule.el);if(el==null){debug("DEBUG: could not find element "+myRule.el);return null;}var err=null;if(el.type){if(el.type=="hidden"||el.type=="text"||el.type=="password"||el.type=="textarea"){err=checkText(el,myRule);}else{if(el.type=="checkbox"){err=checkCheckbox(el,myRule);}else{if(el.type=="select-one"){err=checkSelOne(el,myRule);}else{if(el.type=="select-multiple"){err=checkSelMul(el,myRule);}else{if(el.type=="radio"){err=checkRadio(el,myRule);}else{debug("DEBUG: type "+el.type+" not supported");}}}}}}else{err=checkRadio(el,myRule);}retVal=err;}}}}return retVal;}function checkArguments(R){if(R.length<4){debug("DEBUG: rule requires four arguments at least");return false;}else{if(R[0]==null||R[1]==null){debug("DEBUG: el and ruleName are required");return false;}}return true;}function checkRadio(A,w){var C=null;if(w.ruleName=="required"){var L=A;var J=false;if(isNaN(L.length)&&L.checked){J=true;}else{for(var R=0;R<L.length;R++){if(L[R].checked){J=true;break;}}}if(!J){highlight(A,inputclasserror);C=w.alertMsg;}}else{if(w.ruleName=="equal"){var L=A;var J=false;if(isNaN(L.length)&&L.checked){if(L.value==w.comparisonValue){J=true;}}else{for(var R=0;R<L.length;R++){if(L[R].checked){if(L[R].value==w.comparisonValue){J=true;break;}}}}if(!J){C=w.alertMsg;}}else{if(w.ruleName=="notequal"){var L=A;var J=false;if(isNaN(L.length)&&L.checked){if(L.value!=w.comparisonValue){J=true;}}else{for(var R=0;R<L.length;R++){if(L[R].checked){if(L[R].value!=w.comparisonValue){J=true;break;}}}}if(!J){C=w.alertMsg;}}else{debug("DEBUG: rule "+w.ruleName+" not supported for radio");}}}return C;}function checkText(el,myRule){err=null;if(trimenabled){el.value=strTrim(el.value);}if(myRule.ruleName=="required"){if(el.value==null||el.value==""){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{if(myRule.ruleName=="equal"){err=checkEqual(el,myRule);}else{if(myRule.ruleName=="notequal"){err=checkNotEqual(el,myRule);}else{if(myRule.ruleName=="numeric"){reg=new RegExp("^[0-9]*$");if(!reg.test(el.value)){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{if(myRule.ruleName=="alphabetic"){reg=new RegExp("^[A-Za-z]*$");if(!reg.test(el.value)){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{if(myRule.ruleName=="alphanumeric"){reg=new RegExp("^[A-Za-z0-9]*$");if(!reg.test(el.value)){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{if(myRule.ruleName=="alnumhyphen"){reg=new RegExp("^[A-Za-z0-9-_]*$");if(!reg.test(el.value)){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{if(myRule.ruleName=="alnumhyphenat"){reg=new RegExp("^[A-Za-z0-9-_@]*$");if(!reg.test(el.value)){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{if(myRule.ruleName=="alphaspace"){reg=new RegExp("^[A-Za-z0-9-_ \n\r\t]*$");if(!reg.test(el.value)){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{if(myRule.ruleName=="email"){reg=new RegExp("^(([0-9a-zA-Z]+[-._+&])*[0-9a-zA-Z]+@([-0-9a-zA-Z]+[.])+[a-zA-Z]{2,6}){0,1}$");if(!reg.test(el.value)){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{if(myRule.ruleName=="maxlength"){if(isNaN(myRule.comparisonValue)){debug("DEBUG: comparisonValue for rule "+myRule.ruleName+" not a number");}else{if(el.value.length>myRule.comparisonValue){highlight(el,inputclasserror);err=myRule.alertMsg;}}}else{if(myRule.ruleName=="minlength"){if(isNaN(myRule.comparisonValue)){debug("DEBUG: comparisonValue for rule "+myRule.ruleName+" not a number");}else{if(el.value.length<myRule.comparisonValue){highlight(el,inputclasserror);err=myRule.alertMsg;}}}else{if(myRule.ruleName=="numrange"){reg=new RegExp("^[-+]{0,1}[0-9]*[.]{0,1}[0-9]*$");if(!reg.test(unformatNumber(el.value))){highlight(el,inputclasserror);err=myRule.alertMsg;}else{regRange=new RegExp("^[0-9]+-[0-9]+$");if(!regRange.test(myRule.comparisonValue)){debug("DEBUG: comparisonValue for rule "+myRule.ruleName+" not in format number1-number2");}else{rangeVal=myRule.comparisonValue.split("-");if(eval(unformatNumber(el.value))<eval(rangeVal[0])||eval(unformatNumber(el.value))>eval(rangeVal[1])){highlight(el,inputclasserror);err=myRule.alertMsg;}}}}else{if(myRule.ruleName=="regexp"){reg=new RegExp(myRule.comparisonValue);if(!reg.test(el.value)){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{if(myRule.ruleName=="integer"){err=checkInteger(el,myRule);}else{if(myRule.ruleName=="double"){err=checkDouble(el,myRule);}else{if(myRule.ruleName=="date"){err=checkDate(el,myRule);}else{if(myRule.ruleName=="date_lt"){err=checkDateLessThan(el,myRule,false);}else{if(myRule.ruleName=="date_le"){err=checkDateLessThan(el,myRule,true);}else{if(myRule.ruleName=="keypress"){}else{if(myRule.ruleName=="empty"){if(el.value!=null&&el.value!=""){highlight(el,inputclasserror);err=myRule.alertMsg;}}else{debug("DEBUG: rule "+myRule.ruleName+" not supported for "+el.type);}}}}}}}}}}}}}}}}}}}}}return err;}function checkInteger(R,A){reg=new RegExp("^[-+]{0,1}[0-9]*$");if(!reg.test(R.value)){highlight(R,inputclasserror);return A.alertMsg;}}function checkDouble(A,C){var R=DECIMAL_SEP;reg=new RegExp("^[-+]{0,1}[0-9]*["+R+"]{0,1}[0-9]*$");if(!reg.test(A.value)){highlight(A,inputclasserror);return C.alertMsg;}}function checkDate(A,C){error=null;if(A.value!=""){var R=DATE_FORMAT;ddReg=new RegExp("dd");MMReg=new RegExp("MM");yyyyReg=new RegExp("yyyy");if(!ddReg.test(R)||!MMReg.test(R)||!yyyyReg.test(R)){debug("DEBUG: locale format "+R+" not supported");}else{ddStart=R.indexOf("dd");MMStart=R.indexOf("MM");yyyyStart=R.indexOf("yyyy");}strReg=R.replace("dd","[0-9]{2}").replace("MM","[0-9]{2}").replace("yyyy","[0-9]{4}");reg=new RegExp("^"+strReg+"$");if(!reg.test(A.value)){highlight(A,inputclasserror);error=C.alertMsg;}else{dd=A.value.substring(ddStart,ddStart+2);MM=A.value.substring(MMStart,MMStart+2);yyyy=A.value.substring(yyyyStart,yyyyStart+4);if(!checkddMMyyyy(dd,MM,yyyy)){highlight(A,inputclasserror);error=C.alertMsg;}}}return error;}function checkDateLessThan(w,L,C){error=null;var A=checkDate(w,L)==null?true:false;if(A&&w.value!=""){var R=DATE_FORMAT;ddStart=R.indexOf("dd");MMStart=R.indexOf("MM");yyyyStart=R.indexOf("yyyy");dd=w.value.substring(ddStart,ddStart+2);MM=w.value.substring(MMStart,MMStart+2);yyyy=w.value.substring(yyyyStart,yyyyStart+4);myDate=""+yyyy+MM+dd;strReg=R.replace("dd","[0-9]{2}").replace("MM","[0-9]{2}").replace("yyyy","[0-9]{4}");reg=new RegExp("^"+strReg+"$");var B=L.comparisonValue.indexOf("$")==0?true:false;var J="";if(B){toSplit=L.comparisonValue.substr(1);tmp=toSplit.split(":");if(tmp.length==2){J=this.getField(f,tmp[0]).value;}else{J=this.getField(f,L.comparisonValue.substr(1)).value;}}else{J=L.comparisonValue;}if(!reg.test(J)){highlight(w,inputclasserror);error=L.alertMsg;}else{cdd=J.substring(ddStart,ddStart+2);cMM=J.substring(MMStart,MMStart+2);cyyyy=J.substring(yyyyStart,yyyyStart+4);cDate=""+cyyyy+cMM+cdd;if(C){if(!checkddMMyyyy(cdd,cMM,cyyyy)||myDate>cDate){highlight(w,inputclasserror);error=L.alertMsg;}}else{if(!checkddMMyyyy(cdd,cMM,cyyyy)||myDate>=cDate){highlight(w,inputclasserror);error=L.alertMsg;}}}}else{if(w.value!=""){highlight(w,inputclasserror);error=L.alertMsg;}}return error;}function checkEqual(A,C){error=null;var J=C.comparisonValue.indexOf("$")==0?true:false;var R="";if(J){toSplit=C.comparisonValue.substr(1);tmp=toSplit.split(":");if(tmp.length==2){R=this.getField(f,tmp[0]).value;}else{R=this.getField(f,C.comparisonValue.substr(1)).value;}}else{R=C.comparisonValue;}if(A.value!=R){highlight(A,inputclasserror);error=C.alertMsg;}return error;}function checkNotEqual(A,C){error=null;var J=C.comparisonValue.indexOf("$")==0?true:false;var R="";if(J){toSplit=C.comparisonValue.substr(1);tmp=toSplit.split(":");if(tmp.length==2){R=this.getField(f,tmp[0]).value;}else{R=this.getField(f,C.comparisonValue.substr(1)).value;}}else{R=C.comparisonValue;}if(A.value==R){highlight(A,inputclasserror);error=C.alertMsg;}return error;}function checkddMMyyyy(R,C,A){retVal=true;if((R>31)||(C>12)||(R==31&&(C==2||C==4||C==6||C==9||C==11))||(R>29&&C==2)||(R==29&&(C==2)&&((A%4>0)||(A%4==0&&A%100==0&&A%400>0)))){retVal=false;}return retVal;}function checkCheckbox(R,A){if(A.ruleName=="required"){if(!R.checked){highlight(R,inputclasserror);return A.alertMsg;}}else{if(A.ruleName=="equal"){if(!R.checked||R.value!=A.comparisonValue){highlight(R,inputclasserror);return A.alertMsg;}}else{if(A.ruleName=="notequal"){if(!R.checked||R.value==A.comparisonValue){highlight(R,inputclasserror);return A.alertMsg;}}else{debug("DEBUG: rule "+A.ruleName+" not supported for "+R.type);}}}}function checkSelOne(R,C){if(C.ruleName=="required"){var A=false;var J=R.selectedIndex;if(J>=0&&R.options[J].value){A=true;}if(!A){highlight(R,inputclasserror);return C.alertMsg;}}else{if(C.ruleName=="equal"){var A=false;var J=R.selectedIndex;if(J>=0&&R.options[J].value==C.comparisonValue){A=true;}if(!A){highlight(R,inputclasserror);return C.alertMsg;}}else{if(C.ruleName=="notequal"){var A=false;var J=R.selectedIndex;if(J>=0&&R.options[J].value!=C.comparisonValue){A=true;}if(!A){highlight(R,inputclasserror);return C.alertMsg;}}else{debug("DEBUG: rule "+C.ruleName+" not supported for "+R.type);}}}}function checkSelMul(A,J){if(J.ruleName=="required"){var C=false;opts=A.options;for(var R=0;R<opts.length;R++){if(opts[R].selected&&opts[R].value){C=true;break;}}if(!C){highlight(A,inputclasserror);return J.alertMsg;}}else{if(J.ruleName=="equal"){var C=false;opts=A.options;for(var R=0;R<opts.length;R++){if(opts[R].selected&&opts[R].value==J.comparisonValue){C=true;break;}}if(!C){highlight(A,inputclasserror);return J.alertMsg;}}else{if(J.ruleName=="notequal"){var C=false;opts=A.options;for(var R=0;R<opts.length;R++){if(opts[R].selected&&opts[R].value!=J.comparisonValue){C=true;break;}}if(!C){highlight(A,inputclasserror);return J.alertMsg;}}else{debug("DEBUG: rule "+J.ruleName+" not supported for "+A.type);}}}}function debug(R){if(debugmode){alert(R);}}function strTrim(R){return R.replace(/^\s+/,"").replace(/\s+$/,"");}function makeRules(R){var C=new Array();if(R.length){for(var A=0;A<R.length;A++){C[A]=splitRule(R[A]);}}else{C[0]=splitRule(R);}return C;}function splitRule(A){var R=null;if(A!=undef){params=A.split("|");switch(params.length){case 2:R=new rule(params[0],params[1],null,null,null);break;case 3:if(threeParamRule(params[1])){R=new rule(params[0],params[1],params[2],null,null);}else{if(params[2]=="pre-condition"||params[2]=="post-condition"){R=new rule(params[0],params[1],null,"foo",params[2]);}else{R=new rule(params[0],params[1],null,params[2],null);}}break;case 4:if(threeParamRule(params[1])&&(params[3]=="pre-condition"||params[3]=="post-condition")){R=new rule(params[0],params[1],params[2],"foo",params[3]);}else{R=new rule(params[0],params[1],params[2],params[3],null);}break;default:debug("DEBUG: wrong definition of rule");}}return R;}function threeParamRule(R){return (R=="equal"||R=="notequal"||R=="minlength"||R=="maxlength"||R=="date_lt"||R=="date_le"||R=="implies"||R=="regexp"||R=="numrange"||R=="keypress"||R=="and"||R=="or")?true:false;}function highlight(A,R){if(A!=undef&&inputhighlight){A.className=R;}}function getDefaultMessage(A,R,J,C){if(R.length==0){R=A;}var w=DEFAULT_MSG;if(J=="required"){w=REQUIRED_MSG.replace("{1}",R);}else{if(J=="minlength"){w=MINLENGTH_MSG.replace("{1}",R).replace("{2}",C);}else{if(J=="maxlength"){w=MAXLENGTH_MSG.replace("{1}",R).replace("{2}",C);}else{if(J=="numrange"){w=NUMRANGE_MSG.replace("{1}",R).replace("{2}",C);}else{if(J=="date"){w=DATE_MSG.replace("{1}",R);}else{if(J=="numeric"){w=NUMERIC_MSG.replace("{1}",R);}else{if(J=="integer"){w=INTEGER_MSG.replace("{1}",R);}else{if(J=="double"){w=DOUBLE_MSG.replace("{1}",R);}else{if(J=="equal"){w=EQUAL_MSG.replace("{1}",R).replace("{2}",getComparisonDisplayed(C));}else{if(J=="notequal"){w=NOTEQUAL_MSG.replace("{1}",R).replace("{2}",getComparisonDisplayed(C));}else{if(J=="alphabetic"){w=ALPHABETIC_MSG.replace("{1}",R);}else{if(J=="alphanumeric"){w=ALPHANUMERIC_MSG.replace("{1}",R);}else{if(J=="alnumhyphen"){w=ALNUMHYPHEN_MSG.replace("{1}",R);}else{if(J=="alnumhyphenat"){w=ALNUMHYPHENAT_MSG.replace("{1}",R);}else{if(J=="alphaspace"){w=ALPHASPACE_MSG.replace("{1}",R);}else{if(J=="email"){w=EMAIL_MSG.replace("{1}",R);}else{if(J=="regexp"){w=REGEXP_MSG.replace("{1}",R).replace("{2}",C);}else{if(J=="date_lt"){w=DATE_LT_MSG.replace("{1}",R).replace("{2}",getComparisonDisplayed(C));}else{if(J=="date_le"){w=DATE_LE_MSG.replace("{1}",R).replace("{2}",getComparisonDisplayed(C));}else{if(J=="empty"){w=EMPTY_MSG.replace("{1}",R);}}}}}}}}}}}}}}}}}}}}return w;}function getComparisonDisplayed(R){comparisonDisplayed=R;if(R.substring(0,1)=="$"){R=R.substring(1,R.length);tmp=R.split(":");if(tmp.length==2){comparisonDisplayed=tmp[1];}else{comparisonDisplayed=R;}}return comparisonDisplayed;}function getBrowser(){brs=navigator.userAgent.toLowerCase();var R;if(brs.search(/msie\s(\d+(\.?\d)*)/)!=-1){R="msie";}else{if(brs.search(/netscape[\/\s](\d+([\.-]\d)*)/)!=-1){R="netscape";}else{if(brs.search(/firefox[\/\s](\d+([\.-]\d)*)/)!=-1){R="firefox";}else{R="unknown";}}}return R;}function isKeyAllowed(J,A){retval=false;var R;if(J==8){retval=true;}else{for(var C=0;C<A.length;C++){R=A.charCodeAt(C);if(R==J){retval=true;break;}}}return retval;}function getField(A,C){var R=null;if(A.elements[C]){R=A.elements[C];}else{if(document.getElementById(C)){R=document.getElementById(C);}}return R;}function unformatNumber(A){var R=A.replace(THOUSAND_SEP,"");R=R.replace(DECIMAL_SEP,".");return R;}