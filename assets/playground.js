window.myNamespace = Object.assign({}, window.myNamespace, {
    tabulator: {
        cellLog: function (e, cell, table) {

            res = {
                'row': cell.getRow().getIndex(),
                'column': cell.getColumn().getDefinition(),
                'value': cell.getData(),
                'field': cell.getField()
            }
            //console.log(res)
            table.props.setProps({"cellClick": JSON.stringify(res)})
        },
        buttonDelete: function (cell, formatterParams, onRendered) {
            return "<button type='button' class='btn btn-danger btn-sm' id='" + cell.getValue() + "'><i class='fa fa-trash fa-sm'></i></button>";
        },
        buttonInfo: function (cell, formatterParams, onRendered) {
            return "<button type='button' class='btn btn-info btn-sm' id='" + cell.getValue() + "'><i class='fa fa-info-circle fa-sm'></i></button>";
        },
        buttonGear: function (cell, formatterParams, onRendered) {
            // console.log(cell.getData())
            return "<button type='button' class='btn btn-warning btn-sm' id='" + cell.getValue() + "'><i class='fa fa-cogs fa-sm'></i></button>";
        },
        statusled: function (cell, formatterParams, onRendered) {
            console.log(cell.getData())

            if (cell.getValue() == 'processing')
                return "<span><i class='fa fa-spinner fa-sm text-warning'></i></span>";
            if (cell.getValue() == 'error')
                return "<span><i class='fa fa-exclamation-circle fa-sm text-danger'></i></span>";
            if (cell.getValue() == 'idle')
                return "<span><i class='fa fa-check-circle fa-sm text-success'></i></span>";
            return cell.getData()
        }
    }
});