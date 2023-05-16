displayDiv = document.getElementById("display");

function forCheckBox(selectedButton) {
    // getting checkbox values
    gettingHeader = selectedButton.parentElement.parentElement.parentElement.parentElement.parentElement.children[0].children[0].innerText;
    gettingSubHeader = selectedButton.parentElement.parentElement.previousElementSibling.children[0];
    gettingAllInputText = selectedButton.parentElement.parentElement;
    inputValues = gettingAllInputText.getElementsByTagName("INPUT");
    lastElement = inputValues.length;
    inputCheckboxDict = {}
    // writing checkbox values to dictionary
    for (i=0; i<lastElement; i++) {
        inputPlaceholder = inputValues[i].placeholder;
        checkInputValue = inputValues[i].checked;
        inputCheckboxDict[inputPlaceholder] = checkInputValue;
    }
    // checking if div in display exists
    parentID = selectedButton.parentElement.parentElement.parentElement.parentElement.parentElement.id;
    checkingDivExists = document.getElementById(parentID+"display");
    checkingHeader = document.getElementById(parentID + "header")
    checkingSubHeader = document.getElementById(gettingSubHeader.id+"Subheader");
    checkboxDisplay = document.getElementById(gettingSubHeader.id+"checkboxDisplay");

    if (checkingDivExists) { // if parent display exists
        if(checkingHeader) {
            if (checkingSubHeader) {
                if (checkboxDisplay) {
                    removeAllChildNodes(checkboxDisplay);
                
                    for ([key, value] of Object.entries(inputCheckboxDict)) {
                        if (value!=false) {
                            createText = document.createElement("p");
                            textNode = document.createTextNode(key + ": " + value);
                            createText.appendChild(textNode);
                            checkboxDisplay.appendChild(createText);
                            checkingSubHeader.appendChild(checkboxDisplay);
                            checkingDivExists.appendChild(checkingSubHeader);
                            displayDiv.appendChild(checkingDivExists);
                        }
                        else {
                            continue;
                        }
                    }
                }
                else {
                    console.log("Checkbox display does not exist: ", checkboxDisplay)
                    checkboxDiv = document.createElement("div");
                    checkboxDiv.setAttribute("id", gettingSubHeader.id + "checkboxDisplay");
                    // appending child into displayDiv
                    checkingDivExists.appendChild(checkingSubHeader);
                    displayDiv.appendChild(checkingDivExists);
                    
                    for ([key, value] of Object.entries(inputCheckboxDict)) {
                        if (value!=false) {
                            createText = document.createElement("p");
                            textNode = document.createTextNode(key + ": " + value);
                            createText.appendChild(textNode);
                            checkboxDiv.appendChild(createText);
                            checkingSubHeader.appendChild(checkboxDiv);
                            checkingDivExists.appendChild(checkingSubHeader);
                            displayDiv.appendChild(checkingDivExists);
                        }
                        else {
                            continue;
                        }
                    }
                }
            }
            else {
                createSubHeader = document.createElement("h4");
                textSubHeader = document.createTextNode(gettingSubHeader.innerText); // subheader text
                createSubHeader.appendChild(textSubHeader);
                createSubHeader.setAttribute("id", gettingSubHeader.id + "Subheader");
                // creating input text display div + setting id
                checkboxDiv = document.createElement("div");
                checkboxDiv.setAttribute("id", gettingSubHeader.id + "checkboxDisplay");
                // appending child into displayDiv
                checkingDivExists.appendChild(createSubHeader);
                displayDiv.appendChild(checkingDivExists);
                
                for ([key, value] of Object.entries(inputCheckboxDict)) {
                    if (value!=false) {
                        createText = document.createElement("p");
                        textNode = document.createTextNode(key + ": " + value);
                        createText.appendChild(textNode);
                        checkboxDiv.appendChild(createText);
                        createSubHeader.appendChild(checkboxDiv);
                        checkingDivExists.appendChild(createSubHeader);
                        displayDiv.appendChild(checkingDivExists);
                    }
                    else {
                        continue;
                    }
                }
            }
        }
    }
    else { // if parent display does not exist
        // creating header display div + setting id
        createDiv = document.createElement("div");
        createDiv.setAttribute("id", parentID + "display");
        // creating header
        createHeader = document.createElement("h3");
        textHeader = document.createTextNode(gettingHeader);
        createHeader.appendChild(textHeader);
        createHeader.setAttribute("id", parentID+"header");
        // creating subheader
        createSubHeader = document.createElement("h4");
        textSubHeader = document.createTextNode(gettingSubHeader.innerText);
        createSubHeader.appendChild(textSubHeader);
        createSubHeader.setAttribute("id", gettingSubHeader.id+"Subheader");
        // creating checkbox display div + setting id
        checkboxDiv = document.createElement("div");
        checkboxDiv.setAttribute("id", gettingSubHeader.id + "checkboxDisplay");

        createDiv.appendChild(createSubHeader);
        createDiv.appendChild(createHeader);
        displayDiv.appendChild(createDiv);

        for ([key, value] of Object.entries(inputCheckboxDict)) {
            if (value!=false) {
                createText = document.createElement("p");
                textNode = document.createTextNode(key + ": " + value);
                createText.appendChild(textNode);
                checkboxDiv.appendChild(createText);
                createSubHeader.appendChild(checkboxDiv);
                createDiv.appendChild(createSubHeader);
                displayDiv.appendChild(createDiv);
            }
            else {
                continue;
            }
        }
    }
    // check number of checked checkboxes, if count==0, remove header
    count = 0; // Check number of checked checkboxes
    for ([key, value] of Object.entries(inputCheckboxDict)) {
        if (value!=false) {
            count += 1;
        }
        else {
            continue;
        }
    }

    subheaderInDisplay = document.getElementById(gettingSubHeader.id+"Subheader");
    console.log("getting subheader: ",subheaderInDisplay)

    if (count == 0) {
        if (subheaderInDisplay.parentElement.getElementsByTagName("H4")) {
            for (i=0; i<subheaderInDisplay.parentElement.getElementsByTagName("H4").length; i++) {
                if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[1]) {
                    if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[0]) {
                        if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[0].children.length == 0 && subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[1].children.length == 0) {
                            subheaderInDisplay.remove();
                        }
                    }
                }
                else {
                    if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[0]) {
                        if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[0].children.length == 0) {
                            subheaderInDisplay.parentElement.remove();
                        }
                    }
                }
            }
        }
        else {
            console.log("subheaderInDisplay.parentElement: ", subheaderInDisplay.parentElement)
        }
    }
    changeCCHeader();
}

function forInputTexts(selectedTag) {
    // header text
    gettingHeader = selectedTag.parentElement.parentElement.parentElement.parentElement.parentElement.children[0].children[0].innerText;
    gettingSubHeader = selectedTag.parentElement.parentElement.parentElement.children[0].children[0];
    gettingAllInputText = selectedTag.parentElement.parentElement;
    inputTextValues = gettingAllInputText.getElementsByTagName("INPUT");
    lastElement = inputTextValues.length;
    inputTextDict = {}
    // console.log("header: ", gettingHeader)
    // console.log("subheader: ", gettingSubHeader.id)
    for (i=0; i<lastElement; i++) {
        inputPlaceholder = inputTextValues[i].placeholder;
        inputValue = inputTextValues[i].value;
        if (inputValue != "") {
            inputTextDict[inputPlaceholder] = inputValue;
        }
        else {
            continue;
        }
    }
    // checking if div in display exists
    parentID = selectedTag.parentElement.parentElement.parentElement.parentElement.parentElement.id;
    checkingDivExists = document.getElementById(parentID+"display");
    checkingHeader = document.getElementById(parentID + "header")
    checkingSubHeader = document.getElementById(gettingSubHeader.id+"Subheader");
    checkInputTextDisplay = document.getElementById(gettingSubHeader.id + "inputTextDisplay");

    if (checkingDivExists) { // parentID + display exists
        if (checkingHeader) { // header exists
            if (checkingSubHeader) { // subheader exists, just rewriting all inputs
                if (checkInputTextDisplay) { // inputTextDisplay exists
                    removeAllChildNodes(checkInputTextDisplay);
                
                    for ([key, value] of Object.entries(inputTextDict)) {
                        createText = document.createElement("p");
                        textNode = document.createTextNode(key + ": " + value);
                        createText.appendChild(textNode);
                        checkInputTextDisplay.appendChild(createText);
                        checkingSubHeader.appendChild(checkInputTextDisplay);
                        checkingDivExists.appendChild(checkingSubHeader);
                        displayDiv.appendChild(checkingDivExists);
                    }
                }
                else { // inputTextDisplay does not exist
                    console.log("Checkbox display does not exist: ", checkboxDisplay)
                    inputDisplay = document.createElement("div");
                    inputDisplay.setAttribute("id", gettingSubHeader.id + "inputTextDisplay");
                    // appending child into displayDiv
                    checkingDivExists.appendChild(checkingSubHeader);
                    displayDiv.appendChild(checkingDivExists);
                    
                    for ([key, value] of Object.entries(inputTextDict)) {
                        createText = document.createElement("p");
                        textNode = document.createTextNode(key + ": " + value);
                        createText.appendChild(textNode);
                        inputDisplay.appendChild(createText);
                        checkingSubHeader.appendChild(inputDisplay);
                        checkingDivExists.appendChild(checkingSubHeader);
                        displayDiv.appendChild(createDiv);
                    }
                }
            }
            else { // subheader does not exist, create subheader e.g. when, where
                createSubHeader = document.createElement("h4");
                textSubHeader = document.createTextNode(gettingSubHeader.innerText); // subheader text
                createSubHeader.appendChild(textSubHeader);
                createSubHeader.setAttribute("id", gettingSubHeader.id + "Subheader");
                // creating input text display div + setting id
                inputDisplay = document.createElement("div");
                inputDisplay.setAttribute("id", gettingSubHeader.id + "inputTextDisplay");
                // appending child into displayDiv
                checkingDivExists.appendChild(createSubHeader);
                displayDiv.appendChild(checkingDivExists);
                
                for ([key, value] of Object.entries(inputTextDict)) {
                    createText = document.createElement("p");
                    textNode = document.createTextNode(key + ": " + value);
                    createText.appendChild(textNode);
                    inputDisplay.appendChild(createText);
                    createSubHeader.appendChild(inputDisplay);
                    checkingDivExists.appendChild(createSubHeader);
                    displayDiv.appendChild(createDiv);
                }
            }
        }
    }
    else { // checkingDivExists does not exist
        // creating header display div + setting id
        createDiv = document.createElement("div");
        createDiv.setAttribute("id", parentID + "display");
        // creating header
        createHeader = document.createElement("h3");
        textHeader = document.createTextNode(gettingHeader); // header text
        createHeader.appendChild(textHeader);
        createHeader.setAttribute("id", parentID+"header");
        // creating subheader
        createSubHeader = document.createElement("h4");
        textSubHeader = document.createTextNode(gettingSubHeader.innerText); // subheader text
        createSubHeader.appendChild(textSubHeader);
        createSubHeader.setAttribute("id", gettingSubHeader.id + "Subheader");
        // creating input text display div + setting id
        inputDisplay = document.createElement("div");
        inputDisplay.setAttribute("id", gettingSubHeader.id + "inputTextDisplay");

        createDiv.appendChild(createSubHeader);
        createDiv.appendChild(createHeader);
        displayDiv.appendChild(createDiv);
        
        for ([key, value] of Object.entries(inputTextDict)) {
            createText = document.createElement("p");
            textNode = document.createTextNode(key + ": " + value);
            createText.appendChild(textNode);
            inputDisplay.appendChild(createText);
            createSubHeader.appendChild(inputDisplay);
            createDiv.appendChild(createSubHeader);
            displayDiv.appendChild(createDiv);

        }
    }
    count = 0; // Check number of checked checkboxes
    for ([key, value] of Object.entries(inputTextDict)) {
        if (value!="") {
            count += 1;
        }
        else {
            continue;
        }
    }

    subheaderInDisplay = document.getElementById(gettingSubHeader.id+"Subheader");
    // console.log(subheaderInDisplay, count)

    if (count == 0) {
        if (subheaderInDisplay.parentElement.getElementsByTagName("H4")) {
            for (i=0; i<subheaderInDisplay.parentElement.getElementsByTagName("H4").length; i++) {
                if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[1]) {
                    if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[0]) {
                        if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[0].children.length == 0 && subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[1].children.length == 0) {
                            subheaderInDisplay.remove();
                        }
                    }
                }
                else {
                    if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[0]) {
                        if (subheaderInDisplay.parentElement.getElementsByTagName("H4")[i].children[0].children.length == 0) {
                            subheaderInDisplay.parentElement.remove();
                        }
                    }
                }
            }
        }
        else {
            console.log("subheaderInDisplay.parentElement: ", subheaderInDisplay.parentElement)
        }
    }

    changeCCHeader();
    ccHistory = document.getElementById("CCHistory").value;
    if (ccHistory == "Yes") {
        CCHistory();
    }
    else {
        parentOfHistoryWhen = document.getElementById("CCHistoryWhenLabel").parentElement;
        parentOfHistoryWhen.remove();
        console.log("History When displayif No", document.getElementById("CCHistoryQn2inputTextDisplay").children[1])
        if (document.getElementById("CCHistoryQn2inputTextDisplay").children[1]) {
            document.getElementById("CCHistoryQn2inputTextDisplay").children[1].remove();
        }
    }
    
}

function removeAllChildNodes(parent) {
    while (parent.children[0]) {
        parent.removeChild(parent.firstChild);
    }
}

function Attendance() {
    AttendanceDiv = document.getElementById("Attendancecategories");
    AttendanceSelect = document.getElementById("AttendanceSelect").value;

    topDiv = document.getElementById("topDiv2");
    rfaDiv = document.getElementById("rfaDiv2");
    CCDiv = document.getElementById("CCDiv2");
    oeDiv = document.getElementById("oeDiv2");

    if (AttendanceSelect == "Attended") {
        AttendanceDiv.style.display = "none";
        topDiv.style.display = "grid";
        rfaDiv.style.display = "grid";
        CCDiv.style.display = "grid";
        oeDiv.style.display = "grid";
    }
    else {
        AttendanceDiv.style.display = "grid";
        topDiv.style.display = "none";
        rfaDiv.style.display = "none";
        CCDiv.style.display = "none";
        oeDiv.style.display = "none";
    }
}

function CC() {
    cc = document.getElementById("CCSelect").value;
    ccCategory = document.getElementById("CCcategories");
    OECategory = document.getElementById("OEcategories");
    OEDivHeader = document.getElementById("OE2");
    console.log("CCSelect: ", cc);
    console.log("CCcategories: ", ccCategory, ", display: ", ccCategory.display);
    console.log("OEDiv: ", OEDivHeader, OEDivHeader.innerText)

    if (cc=="Pain") {
        ccCategory.style.display = "grid";
        OECategory.style.display = "grid";
        OEDivHeader.innerText = "O/E: "
    }
    else if (cc=="NIL") {
        ccCategory.style.display = "none";
        OECategory.style.display = "none";
        OEDivHeader.innerText = "O/E: Change C/C to 'Pain' to select O/E";
    }
}

function CCDuration() {
    cc = document.getElementById("CCDuration").value;

    if (cc=="Not Sure") {
        ccCategory.style.display = "grid";
        OECategory.style.display = "grid";
        OEDivHeader.innerText = "O/E: "
    }
    else if (cc=="Not Sure") {
        ccCategory.style.display = "none";
        OECategory.style.display = "none";
        OEDivHeader.innerText = "O/E: Change C/C to 'Pain' to select O/E";
    }
}

function CCHistory() {
    ccHistory = document.getElementById("CCHistory").value;
    HistorySubCategory = document.getElementById("CCHistoryQn2");
    getAllInputText = HistorySubCategory.parentElement.nextElementSibling;
    console.log("getAllInputText: ", getAllInputText)
    if (!document.getElementById("CCHistoryWhenLabel")) {
        createEachInputTextDiv = document.createElement("div");
        createEachInputTextDiv.setAttribute("class", "eachInputText");
        // creating header
        createHistoryYesLabel = document.createElement("label");
        createHistoryYesLabelText = document.createTextNode("When: "); // header text
        createHistoryYesLabel.appendChild(createHistoryYesLabelText);
        createHistoryYesLabel.setAttribute("id", "CCHistoryWhenLabel");
        createHistoryYesLabel.setAttribute("for", "CCHistoryWhen");

        createEachInputTextDiv.appendChild(createHistoryYesLabel)
        
        createHistoryYesInput = document.createElement("input");
        createHistoryYesInput.setAttribute("id", "CCHistoryWhen");
        createHistoryYesInput.setAttribute("type", "text");
        createHistoryYesInput.setAttribute("placeholder", "When");
        createHistoryYesInput.setAttribute("onchange", "forInputTexts(this)");

        createEachInputTextDiv.appendChild(createHistoryYesInput)

        getAllInputText.appendChild(createEachInputTextDiv);
    }
}

function changeCCHeader() { // editing header texts
    CCDiv2Header = document.getElementById("CCDiv2header").innerText;
    // console.log("CCDiv2Header: ", CCDiv2Header);
    CCDiv2HeaderText = CCDiv2Header.split(" ")[0];
    // console.log(CCDiv2Header, CCDiv2HeaderText);
    document.getElementById("CCDiv2header").innerText = CCDiv2HeaderText;
}

function CopyToClipboard() {
    var getDisplayDiv = document.getElementById("display");
    var createRange = document.createRange();
    createRange.selectNode(getDisplayDiv);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(createRange);
    document.execCommand('copy');
    window.getSelection().removeAllRanges();
}


// function gingivitis() {
//     gingivitisDiv = document.getElementById("gingivitisDiv");
//     gin = document.getElementById("gingivitis").value;
//     checkOthers = document.getElementById("gingiOthers");
//     if (!checkOthers) {
//         if (gin=="Others") {
//             optionsInput = document.createElement("INPUT");
//             optionsInput.setAttribute("type", "text");
//             optionsInput.setAttribute("for", "gingivitis");
//             optionsInput.setAttribute("id", "gingiOthers");
//             gingivitisDiv.appendChild(optionsInput);
//         }
//     }
//     else {
//         checkOthers.parentNode.removeChild(checkOthers);
//     }
// }

// function checkHistory() {
//     historyDiv = document.getElementById("historyDiv");
//     checkinghistory = document.getElementById("checkingHistory").value;
//     historyYes = document.getElementById("historyYes");
//     if (!historyYes) {
//         if (checkinghistory=="Yes") {
//             optionsInput = document.createElement("INPUT");
//             optionsInput.setAttribute("type", "text");
//             optionsInput.setAttribute("for", "checkingHistory");
//             optionsInput.setAttribute("id", "historyYes");
//             optionsInput.setAttribute("placeholder", "When did it happen before?");

//             historyDiv.appendChild(optionsInput);
//         }
//     }
//     else {
//         historyYes.parentNode.removeChild(historyYes);
//     }
// }

// function RFA() {
//     RFADiv = document.getElementById("RFADiv")
//     rfa = document.getElementById("RFA").value;
//     RFAOthers = document.getElementById("RFAOthers");
//     if (!RFAOthers) {
//         if (rfa=="Others") {
//             optionsInput = document.createElement("INPUT");
//             optionsInput.setAttribute("type", "text");
//             optionsInput.setAttribute("for", "rfa");
//             optionsInput.setAttribute("id", "RFAOthers");
//             RFADiv.appendChild(optionsInput);
//         }
//     }
//     else {
//         RFAOthers.parentNode.removeChild(RFAOthers);
//     }
// }



// function worsenFactorPosture() {
//     posture = document.getElementById("posture").checked;
//     forposture = document.getElementById("forPosture");

//     if (posture == true) {
//         console.log("Posture is true!");
//         forposture.style.display = "grid";
//     }
//     else {
//         console.log("Posture is false!");
//         forposture.style.display = "none";
//     }

// }

// function Attendance() {
//     attendanceDiv = document.getElementById("notAttendingDiv");
//     noShow = document.getElementById("attendance").value;
//     notAttending = document.getElementById("notAttending");


//     if (noShow=="Failed to Attend" || noShow=="Unable to Attend") {

//         if (!notAttending) {
//             space = document.createElement("BR");

//             reasonLabel = document.createElement("LABEL");
//             reasonLabel.setAttribute("for", "attendance");
//             reasonLabel.setAttribute("id", "reasonLabel");
//             reasonLabel.innerText = "Not Attending Reason: ";

//             reason = document.createElement("INPUT");
//             reason.setAttribute("type", "text");
//             reason.setAttribute("for", "attendance");
//             reason.setAttribute("id", "notAttending");

//             rescheduledLabel = document.createElement("LABEL");
//             rescheduledLabel.setAttribute("for", "attendance");
//             rescheduledLabel.setAttribute("id", "rescheduledLabel");
//             rescheduledLabel.innerText = "Rescheduled Date: ";

//             rescheduled = document.createElement("INPUT");
//             rescheduled.setAttribute("type", "date");
//             rescheduled.setAttribute("for", "attendance");
//             rescheduled.setAttribute("id", "rescheduling");

//             attendanceDiv.appendChild(space);
//             attendanceDiv.appendChild(reasonLabel);
//             attendanceDiv.appendChild(reason);
//             attendanceDiv.appendChild(space);
//             attendanceDiv.appendChild(rescheduledLabel);
//             attendanceDiv.appendChild(rescheduled);
//         }
//     }
//     else if (noShow=="Attended") {
//         removeAllChildNodes(attendanceDiv)

//         notAttending.parentNode.removeChild(notAttending);
//     }
// }

// function submit() {
//     main = document.getElementById("main");
//     topLabel = document.getElementById("topLabel").innerText;
//     Top = document.getElementById("top").value;
//     attendanceLabel = document.getElementById("attendanceLabel").innerText;
//     attendance = document.getElementById("attendance").value;

//     RFALabel = document.getElementById("RFALabel").innerText;
//     rfa = document.getElementById("RFA").value;

//     gingerLabel = document.getElementById("gingiLabel").innerText;
//     ginger = document.getElementById("gingivitis").value;

//     CleanTeethLabel = document.getElementById("CleanTeethLabel").innerText;
//     cleanTeeth = document.getElementById("CleanTeeth").value;

//     CCLabel = document.getElementById("CCLabel").innerText;
//     cc = document.getElementById("CC").value;

//     wherePain = document.getElementsByClassName("WherePain")[0]
//     whenPain = document.getElementsByClassName("WhenPain")[0]

//     painDuration = document.getElementById("painDuration").value;

//     painScore = document.getElementById("painScore").value;

//     historyLabel = document.getElementById("historyLabel").innerText;
//     historyValue = document.getElementById("checkingHistory").value;

//     worsenFactor = document.getElementsByClassName("WorsenFactorsDiv")[0];

//     betterFactor = document.getElementsByClassName("BetterFactorsDiv")[0];

//     affectsSleeping = document.getElementsByClassName("SleepAffectingDiv")[0];

//     possibleCause = document.getElementsByClassName("PossibleCauseDiv")[0];
    
//     // For Others value in C/C, put here
//     CCWhereOthers = document.getElementById("CCWhereOthers").value;
//     CCWhenOthers = document.getElementById("CCWhenOthers").value;
//     CCBetterFactorsOthers = document.getElementById("betterFactorsOthers").value;
//     SleepingOthers = document.getElementById("SleepingOthers").value;
//     possibleCauseOthers = document.getElementById("possibleOthers").value;

//     display = document.getElementById("display");

//     removeAllChildNodes(display);

//     wherePainList = [];
//     whenPainList = [];
//     worsenFactorList = [];
//     betterFactorList = [];
//     affectsSleepingList = [];
//     possibleCauseList = [];
//     CCOthersList = [];

    

//     if (attendance!=="Attended") {
//         attendedDisplay = document.createElement("p");
//         attendedDisplayText = document.createTextNode(attendanceLabel + " " + attendance);
//         attendedDisplay.appendChild(attendedDisplayText);

//         notAttendingReason = document.getElementById("notAttending").value;
//         rescheduling = document.getElementById("rescheduling").value;

//         reason = document.createElement("p");
//         reasonText = document.createTextNode("Reason: " + notAttendingReason);
//         reason.appendChild(reasonText);

//         reschedule = document.createElement("p");
//         rescheduleText = document.createTextNode("Reschedule to: " + rescheduling);
//         reschedule.appendChild(rescheduleText)

//         display.appendChild(attendedDisplay);
//         display.appendChild(reason);
//         display.appendChild(reschedule);
//     }
//     else {
//         if (ginger=="Others") {
//             gingiOthers = document.getElementById("gingiOthers").value;
//             ginger = gingiOthers;
//         }

//         if (rfa=="Others") {
//             RFAOthers = document.getElementById("RFAOthers").value;
//             rfa = RFAOthers;
//         }

//         if (cc=="Pain") {
//             // Check Pain Score value if its 0 <= Pain Score <= 10
//             if (painScore > 10 || painScore < 0) {
//                 alert("Pain Score value must be between 0 and 10!!!");
//                 return false;
//             }

//             // For wherePain
//             for (i=0; i < wherePain.getElementsByTagName("INPUT").length-2; i++) {
//                 if (wherePain.getElementsByTagName("INPUT")[i].checked == true) {
//                     wherePainListKeys = wherePain.getElementsByTagName("INPUT")[i].placeholder;
//                     wherePainList.push(wherePainListKeys);
//                 }
//             }
//             // Check ToothHurts value
//             CCToothHurts = document.getElementById("toothPain").value;

//             // Check WherePain Others value
//             // if (wherePain.getElementsByTagName("INPUT")[5].value !== "") {
//             //     CCWhereOthers = document.getElementById("CCWhereOthers").value;
//             //     CCOthersList.push(CCWhereOthers);
//             // }

//             // For whenPain
//             for (i=0; i < whenPain.getElementsByTagName("INPUT").length-1; i++) {
//                 if (whenPain.getElementsByTagName("INPUT")[i].checked == true) {
//                     whenPainListKeys = whenPain.getElementsByTagName("INPUT")[i].placeholder;
//                     console.log("when pain values", whenPainListKeys)
//                     whenPainList.push(whenPainListKeys);
//                 }
//             }
//             // For Triggered by value
//             if (whenPain.getElementsByTagName("INPUT")[7].value !== undefined){
//                 whenTrigger = document.getElementById("whenTrigger").value;
//             }
//             // For WhenPain Others value
//             // if (whenPain.getElementsByTagName("INPUT")[8].value !== "") {
//             //     CCWhenOthers = document.getElementById("CCWhenOthers").value;
//             //     CCOthersList.push(CCWhenOthers);
//             // }

//             // For WorsenFactor
//             forPosture = document.getElementById("posture").checked;
//             if (forPosture == true) {
//                 if (document.getElementById("standing").checked !== true && document.getElementById("lyingDown").checked !== true) {
//                     alert("Posture was selected but neither options were checked!");
//                     return false;
//                 }

//                 for (i=0; i < worsenFactor.getElementsByTagName("INPUT").length; i++) {
//                     if (worsenFactor.getElementsByTagName("INPUT")[i].checked == true) {
//                         worsenFactorListKeys = worsenFactor.getElementsByTagName("INPUT")[i].placeholder;
//                         if (worsenFactorListKeys !== "Posture") {
//                             worsenFactorList.push(worsenFactorListKeys);
//                         }
//                     }
//                 }
//             }
//             else {
//                 for (i=0; i < worsenFactor.getElementsByTagName("INPUT").length-2; i++) {
//                     if (worsenFactor.getElementsByTagName("INPUT")[i].checked == true) {
//                         worsenFactorListKeys = worsenFactor.getElementsByTagName("INPUT")[i].placeholder;
//                         worsenFactorList.push(worsenFactorListKeys);
//                     }
//                 }
//             }

//             // For BetterFactor
//             for (i=0; i < betterFactorsDiv.getElementsByTagName("INPUT").length-3; i++) {
//                 if (betterFactorsDiv.getElementsByTagName("INPUT")[i].checked == true) {
//                     betterFactorListKeys = betterFactorsDiv.getElementsByTagName("INPUT")[i].placeholder;
//                     betterFactorList.push(betterFactorListKeys);
//                 }
//             }
//             console.log("Better factors: ", betterFactorList)

//             // For medication
//             betterMedication = document.getElementById("medication").value;

//             // For avoiding worsening factor
//             BetterWhenAvoiding = document.getElementById("avoidingWorsenFactor").value;

//             // Check betterFactors Others value
//             // if (betterFactorsDiv.getElementsByTagName("INPUT")[6].value !== "") {
//             //     CCBetterFactorsOthers = document.getElementById("betterFactorsOthers").value;
//             //     CCOthersList.push(CCBetterFactorsOthers);
//             // }

//             // For AffectSleeping
//             for (i=0; i < affectsSleeping.getElementsByTagName("INPUT").length-1; i++) {
//                 if (affectsSleeping.getElementsByTagName("INPUT")[i].checked == true) {
//                     affectsSleepingListKeys = affectsSleeping.getElementsByTagName("INPUT")[i].placeholder;
//                     console.log("when pain values", affectsSleepingList)
//                     affectsSleepingList.push(affectsSleepingListKeys);
//                 }
//             }

//             // SleepingOthers
//             // if (affectsSleeping.getElementsByTagName("INPUT")[3].value !== "") {
//             //     SleepingOthers = document.getElementById("SleepingOthers").value;
//             //     CCOthersList.push(SleepingOthers);
//             // }

//             // For possible causes
//             for (i=0; i < possibleCause.getElementsByTagName("INPUT").length-1; i++) {
//                 if (possibleCause.getElementsByTagName("INPUT")[i].checked == true) {
//                     possibleCauseListKeys = possibleCause.getElementsByTagName("INPUT")[i].placeholder;
//                     console.log("when pain values", possibleCauseList)
//                     possibleCauseList.push(possibleCauseListKeys);
//                 }
//             }

//             // possibleOthers
//             // if (possibleCause.getElementsByTagName("INPUT")[3].value !== "") {
//             //     possibleCauseOthers = document.getElementById("possibleOthers").value;
//             //     CCOthersList.push(possibleCauseOthers);
//             // }
//         }

//         display1 = document.createElement("p");
//         display1Text = document.createTextNode(attendanceLabel + " " + attendance);
//         display1.appendChild(display1Text);

//         display2 = document.createElement("p");
//         display2Text = document.createTextNode(topLabel + " " + Top);
//         display2.appendChild(display2Text);

//         if (ginger !== "") {
//             display3 = document.createElement("p");
//             display3Text = document.createTextNode(gingerLabel + " " + ginger);
//             display3.appendChild(display3Text);
//         }
//         else {
//             alert("You did not fill up gingivitis!");
//             return false;
//         }

//         if (cleanTeeth !== "") {
//             display4 = document.createElement("p");
//             display4Text = document.createTextNode(CleanTeethLabel + " " + cleanTeeth);
//             display4.appendChild(display4Text);
//         }
//         else {
//             alert("You did not fill up Teeth Cleanliness!");
//             return false;
//         }

//         display5 = document.createElement("p");
//         display5Text = document.createTextNode(RFALabel + " " + rfa);
//         display5.appendChild(display5Text);

//         display6 = document.createElement("p");
//         display6Text = document.createTextNode(CCLabel + " " + cc);
//         display6.appendChild(display6Text);

//         if (cc == "Pain") {
//             if (Object.keys(wherePainList)[0] !== undefined) {
//                 display7 = document.createElement("p");
//                 display7Text = document.createTextNode("Where does it hurt: " + wherePainList + ", Other comments: " + CCWhereOthers);
//                 display7.appendChild(display7Text);
//             }
//             else {
//                 alert("You have not chosen anything for 'Where does it hurt?'");
//                 return false;
//             }

//             if (Object.keys(whenPainList)[0] !== undefined) {
//                 display8 = document.createElement("p");
//                 display8Text = document.createTextNode("When does it hurt: " + whenPainList + ", Other comments: " + CCWhenOthers);
//                 display8.appendChild(display8Text);
//             }
//             else {
//                 alert("You have not chosen anything for 'When does it hurt?'");
//                 return false;
//             }
            
//             console.log("when pain list: ", whenPainList)

//             if (CCToothHurts !== "") {
//                 display9 = document.createElement("p");
//                 display9Text = document.createTextNode("Which tooth hurts: " + CCToothHurts);
//                 display9.appendChild(display9Text);
//             }
//             else {
//                 alert("Which tooth hurts is not filled in!!!");
//                 display9 = document.createElement("p");
//                 display9.setAttribute("display", "none");
//             }

//             if (whenTrigger !== null) {
//                 display10 = document.createElement("p");
//                 display10Text = document.createTextNode("Triggered by: " + whenTrigger);
//                 display10.appendChild(display10Text);
//             }

//             if (painDuration !== "") {
//                 display11 = document.createElement("p");
//                 display11Text = document.createTextNode("Pain Duration: " + painDuration);
//                 display11.appendChild(display11Text);
//             }
//             else {
//                 alert("Pain Duration is not filled in!!!");
//                 display11 = document.createElement("p");
//                 display11.setAttribute("display", "none");
//             }

//             if (painScore !== "") {
//                 display12 = document.createElement("p");
//                 display12Text = document.createTextNode("Pain Score: " + painScore);
//                 display12.appendChild(display12Text);
//             }
//             else {
//                 alert("Pain Score is not filled in!!!");
//                 display12 = document.createElement("p");
//                 display12.setAttribute("display", "none");
//             }

//             if (historyValue=="Yes") {
//                 newHistoryValue = document.getElementById("historyYes").value;
//                 // historyValue = newHistoryValue;

//                 if (newHistoryValue !== "") {
//                     display13 = document.createElement("p");
//                     display13Text = document.createTextNode(historyLabel + " Yes, " + newHistoryValue);
//                     display13.appendChild(display13Text);
//                 }
//                 else {
//                     alert("You did not fill up History!");
//                     return false;
//                 }
//             }
//             else {
//                 display13 = document.createElement("p");
//                 display13Text = document.createTextNode(historyLabel + " " + historyValue);
//                 display13.appendChild(display13Text);
//             }

//             if (Object.keys(worsenFactorList)[0] !== undefined) {
//                 display14 = document.createElement("p");
//                 display14Text = document.createTextNode("What makes it worse: " + worsenFactorList);
//                 display14.appendChild(display14Text);
//             }
//             else {
//                 alert("You have not chosen anything for 'What makes it worse?'");
//                 return false;
//             }

//             if (Object.keys(betterFactorList)[0] !== undefined) {
//                 display15 = document.createElement("p");
//                 display15Text = document.createTextNode("What makes it better: " + betterFactorList + ", Other comments: " + CCBetterFactorsOthers);
//                 display15.appendChild(display15Text);
//             }
//             else {
//                 alert("You have not chosen anything for 'What makes it better?'");
//                 return false;
//             }

//             if (betterMedication !== "") {
//                 display16 = document.createElement("p");
//                 display16Text = document.createTextNode("Medication that helps with pain: " + betterMedication);
//                 display16.appendChild(display16Text);
//             }
//             else {
//                 alert("'Medication that makes it better' is not filled in!!!");
//                 display16 = document.createElement("p");
//                 display16.setAttribute("display", "none");
//             }

//             if (Object.keys(affectsSleepingList)[0] !== undefined) {
//                 display17 = document.createElement("p");
//                 display17Text = document.createTextNode("Does it affect Sleeping: " + affectsSleepingList + ", Other comments: " + SleepingOthers);
//                 display17.appendChild(display17Text);
//                 }
//             else {
//                 alert("You have not chosen anything for 'Does it affect sleep?'!!!");
//                 display17 = document.createElement("p");
//                 display17.setAttribute("display", "none");
//             }

//             if (Object.keys(possibleCauseList)[0] !== undefined) {
//                 display18 = document.createElement("p");
//                 display18Text = document.createTextNode("Possible Causes: " + possibleCauseList + ", Other comments: " + possibleCauseOthers);
//                 display18.appendChild(display18Text);
//                 }
//             else {
//                 alert("You have not chosen anything for 'Possible causes?'!!!");
//                 display18 = document.createElement("p");
//                 display18.setAttribute("display", "none");
//             }

//             // if (Object.keys(CCOthersList)[0] !== undefined) {
//             // display22 = document.createElement("p");
//             // display22Text = document.createTextNode("Other comments: " + CCOthersList);
//             // display22.appendChild(display22Text);
//             // }
//             // else {
//             //     display22 = document.createElement("p");
//             //     display22.setAttribute("display", "none");
//             // }

//             display.appendChild(display1);
//             display.appendChild(display2);
//             display.appendChild(display3);
//             display.appendChild(display4);
//             display.appendChild(display5);
//             display.appendChild(display6);
//             display.appendChild(display7);
//             display.appendChild(display8);
//             display.appendChild(display9);
//             display.appendChild(display10);
//             display.appendChild(display11);
//             display.appendChild(display12);
//             display.appendChild(display13);
//             display.appendChild(display14);
//             display.appendChild(display15);
//             display.appendChild(display16);
//             display.appendChild(display17);
//             display.appendChild(display18);
//             // display.appendChild(display19);
//             // display.appendChild(display20);
//             // display.appendChild(display21);
//             // display.appendChild(display22);
//         }
//         else {
//             display7 = document.createElement("p");
//             display7.setAttribute("display", "none");

//             display8 = document.createElement("p");
//             display8.setAttribute("display", "none");

//             display9 = document.createElement("p");
//             display9.setAttribute("display", "none");

//             display10 = document.createElement("p");
//             display10.setAttribute("display", "none");

//             display11 = document.createElement("p");
//             display11.setAttribute("display", "none");

//             display12 = document.createElement("p");
//             display12.setAttribute("display", "none");

//             display13 = document.createElement("p");
//             display13.setAttribute("display", "none");

//             display14 = document.createElement("p");
//             display14.setAttribute("display", "none");

//             display15 = document.createElement("p");
//             display15.setAttribute("display", "none");
            
//             display16 = document.createElement("p");
//             display16.setAttribute("display", "none");

//             display17 = document.createElement("p");
//             display17.setAttribute("display", "none");

//             display18 = document.createElement("p");
//             display18.setAttribute("display", "none");

//             // display19 = document.createElement("p");
//             // display19.setAttribute("display", "none");

//             // display20 = document.createElement("p");
//             // display20.setAttribute("display", "none");

//             // display21 = document.createElement("p");
//             // display21.setAttribute("display", "none");

//             // display22 = document.createElement("p");
//             // display22.setAttribute("display", "none");

//             display.appendChild(display1);
//             display.appendChild(display2);
//             display.appendChild(display3);
//             display.appendChild(display4);
//             display.appendChild(display5);
//             display.appendChild(display6);
//             display.appendChild(display7);
//             display.appendChild(display8);
//             display.appendChild(display9);
//             display.appendChild(display10);
//             display.appendChild(display11);
//             display.appendChild(display12);
//             display.appendChild(display13);
//             display.appendChild(display14);
//             display.appendChild(display15);
//             display.appendChild(display16);
//             display.appendChild(display17);
//             display.appendChild(display18);
//             // display.appendChild(display19);
//             // display.appendChild(display20);
//             // display.appendChild(display21);
//             // display.appendChild(display22);
//         }
//     }
// }

// function removeAllChildNodes(parent) {
//     while (parent.firstChild) {
//         parent.removeChild(parent.firstChild);
//     }
// }