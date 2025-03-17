// 아파트 이름 필터
function filterByArticleName() {
    var selectedValue = document.getElementById("articleNameFilter").value.trim().toLowerCase();
    var rows = document.getElementById("articlesTable").getElementsByTagName("tr");

    var showGroup = false;  // 그룹이 보여야 하는지 여부
    var currentGroupName = "";  // 현재 그룹 이름

    console.log("Selected Value:", selectedValue);

    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];

        // 그룹 헤더인 경우
        if (row.classList.contains("group-header")) {
            currentGroupName = row.innerText.trim().toLowerCase().replace(/[^a-z가-힣\s1-9🔺🔻개]/g, "");  // 그룹 이름 설정
            currentGroupName = currentGroupName.replace(/\s*\d+개\s*$/, "");  // 매물 수 제거로 currentGroupName, currentGroupName 일치하는지 확인
            console.log("Current Group Name:", currentGroupName);

            // 선택된 값이 비어있거나, 그룹 이름과 선택된 값이 일치하는 경우
            showGroup = (selectedValue === "" || currentGroupName === selectedValue);
            console.log("Show Group:", showGroup);

            // 그룹 헤더의 display 설정
            row.style.display = showGroup ? "" : "none";

            // 그룹 항목들의 display 설정
            var nextRow = row.nextElementSibling;
            while (nextRow && !nextRow.classList.contains("group-header")) {
                nextRow.style.display = showGroup ? "" : "none";
                nextRow = nextRow.nextElementSibling;
            }
        }
    }
}

// 검색 필터 추가
function filterTable() {
    var input = document.getElementById("searchInput");
    var filter = input.value.trim().toLowerCase();
    var rows = document.getElementById("articlesTable").getElementsByTagName("tr");

     // x 버튼을 숨기거나 나타내는 로직
     var clearBtn = document.getElementById("clearBtn");
     if (filter !== "") {
         clearBtn.style.display = "block"; // 텍스트가 있으면 버튼을 보이게 함
     } else {
         clearBtn.style.display = "none"; // 텍스트가 없으면 버튼을 숨김
     }

    
    for (var i = 0; i < rows.length; i++) { // i = 1 → i = 0 으로 수정
        var row = rows[i];
        var textContent = row.innerText.toLowerCase(); // 여기서 textContent 정의

        if (filter === "") {
            row.style.display = "";
            removeHighlights(row);
        } else if (textContent.includes(filter)) {
            row.style.display = "";
            highlightText(row, filter);
        } else {
            row.style.display = "none";
        }
    }
}

// 검색어 삭제 기능
function clearSearch() {
    var input = document.getElementById("searchInput");
    input.value = "";  // 입력 필드 비우기
    filterTable();     // 테이블 필터링 재실행
}

// 검색 텍스트 하이라이트 
function highlightText(row, keyword) {
    if (!keyword) return;

    var regex = new RegExp(`(${keyword})`, "gi");
    removeHighlights(row);

    function wrapMatch(node) {
        if (node.nodeType === 3) {
            var match = node.nodeValue.match(regex);
            if (match) {
                var replacedText = node.nodeValue.replace(regex, '<span class="highlight">$1</span>');
                var tempDiv = document.createElement("div");
                tempDiv.innerHTML = replacedText;

                var fragment = document.createDocumentFragment();
                while (tempDiv.firstChild) {
                    fragment.appendChild(tempDiv.firstChild);
                }
                node.parentNode.replaceChild(fragment, node);
            }
        } else if (node.nodeType === 1) {
            for (var i = node.childNodes.length - 1; i >= 0; i--) {
                wrapMatch(node.childNodes[i]);
            }
        }
    }

    wrapMatch(row);
}


function removeHighlights(row) {
    var spans = row.querySelectorAll(".highlight");
    spans.forEach(span => {
        span.outerHTML = span.innerHTML; // span 태그만 제거하고 내용 유지
    });
}
