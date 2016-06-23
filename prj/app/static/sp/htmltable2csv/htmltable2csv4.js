/* downloade:http://www.kunalbabre.com/projects/table2CSV.php */
/*for dh*/

jQuery.fn.table2CSV4 = function(options) {
    var options = jQuery.extend({
        separator: ',',
        header: [],
        delivery: 'popup' // popup, value
    },
    options);

    var csvData = [];
    var headerArr = [];
    var el = this;

    //header
    var numCols = options.header.length;
    var tmpRow = []; // construct header avalible array

    if (numCols > 0) {
        for (var i = 0; i < numCols; i++) {
            tmpRow[tmpRow.length] = formatData(options.header[i]);
        }
    } else {
        $(el).find('th').each(function() {
            if ($(this).css('display') != 'none') tmpRow[tmpRow.length] = formatData($(this).html());
        });
    }

    row2CSV(tmpRow);

    // actual data
    $(el).find('tr').each(function() {        
        var tmpRow = [];
        $(this).find('td').each(function() {      //这里冯牧修改
            
            if ($(this).css('display') != 'none'){
                
                tmpRow[tmpRow.length] = formatData($(this).html())
            };
        });
        row2CSV(tmpRow);
    });
    if (options.delivery == 'popup') {
        var mydata = csvData.join('\n');
        return popup(mydata);
    } else {
        var mydata = csvData.join('\n');
        var list = csv2list(mydata)
        var list2 = setformatlist(list, 3, 6)  //对应商品代码，订货数量
        mydata = list2csv(list2)
        return mydata;
    }
    
    function csv2list(csvstr) {
        var list1 = csvstr.split("\n")
        var list2 = []
        var li
        if (list1.length > 0) {
            for (li in list1) {
                li_list = list1[li].split("\t")
                list2.push(li_list)
            }
        }
        list2.shift()
        return list2
    }
    
    function delitem(fmlist, index){
        var li
        if (fmlist.length>0){
            for (li in fmlist){
                fmlist[li].splice(index, 1)
            }
        }
        return fmlist
    }
    
    function setformatlist(fmlist, index1, index2){
        var li
        var newlist = []
        if (fmlist.length>0){
            for (li in fmlist){
                newlist.push([fmlist[li][index1], fmlist[li][index2]])
            }
        }
        return newlist
    }
    
    function list2csv(list){
        var li
        var mystr
        var list1 = []
        var csvstr
        for (li in list) {
            mystr = list[li].join("\t")
            list1.push(mystr)
        }
        csvstr = list1.join("\r\n")
        return csvstr
    }

    function row2CSV(tmpRow) {
        var tmp = tmpRow.join('') // to remove any blank rows
        // alert(tmp);
        if (tmpRow.length > 0 && tmp != '') {
            var mystr = tmpRow.join(options.separator);
            //alert(mystr)
            csvData[csvData.length] = mystr;
        }
    }
    function formatData(input) {
        // replace " with “
        
        if (input.slice(1,6)==='input'){
            if ($(input).attr("checked")){
                return '1'
            } else {
                return '0'
            }
        }    //冯牧增加
        
        var regexp = new RegExp(/["]/g);
        var output = input.replace(regexp, "“");
        //HTML
        var regexp = new RegExp(/\<[^\<]+\>/g);
        var output = output.replace(regexp, "");
        if (output == "") return '';
        return output ;    //这里冯牧修改
    }
    function popup(data) {
        var generator = window.open('', 'csv', 'height=400,width=600');
        generator.document.write('<html><head><title>CSV</title>');
        generator.document.write('</head><body >');
        generator.document.write('<textArea cols=70 rows=15 wrap="off" >');
        generator.document.write(data);
        generator.document.write('</textArea>');
        generator.document.write('</body></html>');
        generator.document.close();
        return true;
    }
};


