
$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
    var actions = $("table td:last-child").html();
    var act = 0
    // Append table with add row form on add new button click
    $(".add-new").click(function () {
        $(this).attr("disabled", "disabled");
        var index = $("table tbody tr:last-child").index();
        var id = parseInt($("table tbody tr:last-child").find("td:eq(0)").text()) + 1
        console.log(id)
        var row = '<tr>' +
            '<td>' + id + '</td>' +
            '<td><input type="text" class="form-control" name="username" id="username"></td>' +
            '<td><input type="text" class="form-control" name="password" id="password"></td>' +
            '<td><input type="text" class="form-control" name="status" id="status"></td>' +
            '<td></td>' +
            '<td>' + actions + '</td>' +
            '</tr>';
        $("table").append(row);
        $("table tbody tr").eq(index + 1).find(".add, .edit").toggle();
        $('[data-toggle="tooltip"]').tooltip();
        act = 1
    });
    // Add row on add button click
    $(document).on("click", ".add", function () {

        var empty = false;
        var input = $(this).parents("tr").find('input[type="text"]');
        var id = $(this).parents("tr").find("td:eq(0)").text()
        var username = input[0].value
        var password = input[1].value
        var status = input[2].value
        input.each(function () {
            if (!$(this).val() || $(this).val() == "**********") {
                $(this).addClass("error");
                empty = true;
            } else {
                $(this).removeClass("error");
            }
        });
        $(this).parents("tr").find(".error").first().focus();
        if (!empty) {
            console.log("act :" + act)
            var data = { 'id': id, 'username': username, 'password': password, 'status': status, 'act': act };
            console.log(data)
            $.ajax({
                data: data,
                url: '/updateUser/',
                method: 'POST',
                success: function (data) {
                    // location.reload(true)

                }
            });
            input[1].value = "**********"
            input.each(function () {
                // var anchor_id = document.getElementsByClassName("card-title anchor-id")[0].innerText;
                // var password = $(this).parents("tr").find("td:eq(0)").text()

                $(this).parent("td").html($(this).val());
                // $(this).parent("td").html($(this).val());
            });

            $(this).parents("tr").find(".add, .edit").toggle();
            $(".add-new").removeAttr("disabled");

        }
    });
    // Edit row on edit button click
    $(document).on("click", ".edit", function () {
        // console.log($(this).parents("tr").find("td:eq(1),td:eq(2),td:eq(3)"))
        $(this).parents("tr").find("td:eq(1),td:eq(2),td:eq(3)").each(function () {
            // $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
            $(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
        });
        // $(this).parents("tr").find("td:eq(1),td:eq(2),td:eq(3)")
        $(this).parents("tr").find(".add, .edit").toggle();
        $(".add-new").attr("disabled", "disabled");
        act = 0
    });
    // Delete row on delete button click
    // $(document).on("click", ".delete", function () {
    //     $(this).parents("tr").remove();
    //     $(".add-new").removeAttr("disabled");
    // });
});
