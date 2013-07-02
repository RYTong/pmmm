/**
 * Created by IntelliJ IDEA.
 * User: chenming
 * Date: 11-11-18
 * Time: 下午2:02
 * To change this template use File | Settings | File Templates.
 */

function exportTableToExcel(table_id){
  var o_AXO = new ActiveXObject("Excel.Application");
  var o_WB;
  var o_Sheet;
  try{
    o_WB = o_AXO.Workbooks.Add();
    //激活当前sheet
    o_Sheet = o_WB.ActiveSheet;
  }catch(err){
    alert("仅适用于IE浏览器,同时请确认已经安装好Excel软件");
    return false;
  }

  var o_table = document.getElementById(table_id);
  var row_len = o_table.rows.length;

  for (i = 0; i < row_len; i++)
  {
      var cell_len = o_table.rows[i].cells.length;

      for (j = 0; j < cell_len; j++)
      {
        var cellText = o_table.rows[i].cells[j].innerText;
         o_Sheet.Cells(i + 1, j + 1).value = cellText;
      }
  }
    o_AXO.Visible = true;
}