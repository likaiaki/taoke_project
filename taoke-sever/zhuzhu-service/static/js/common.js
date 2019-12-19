let qiniu_host = 'http://upload.qiniup.com/';
let title = '';
let url = '';

let update_button = function ($, table) {
    let checkeds = table.checkStatus('table');
    if (checkeds.data.length > 0) {
        $(".must-select").attr("disabled", false).removeClass('layui-btn-disabled');
    } else {
        $(".must-select").attr("disabled", true).addClass('layui-btn-disabled');
    }
};

let checked_ids = function (table) {
    let checked = table.checkStatus('table');
    let ids = [];
    for (let data of checked.data) {
        ids.push(data.id);
    }
    return ids.join(',');
};

let init = function ($, layer, form, table, upload, dic) {

    $(document).on('click', '#refresh-btn', function () {
        window.location.reload();
    });

    $(document).on('mouseover mouseout', 'a.cover', function (e) {
        if (e.type === "mouseover") {
            $("<img id='image_preview' class='float-preview' src='" + this.href + "' alt='' />").appendTo("body");
            $("#image_preview").fadeIn("fast");
        } else if (e.type === "mouseout") {
            $("#image_preview").remove();
        }
    });

    $(document).on('mouseover mouseout', 'a.video', function (e) {
        if (e.type === "mouseover") {
            $("<video id='video_preview' class='float-preview' autoplay='autoplay' src='" + this.href + "' ></video>").appendTo("body");
            $("#video_preview").fadeIn("fast");
        } else if (e.type === "mouseout") {
            $("#video_preview").remove();
        }
    });

    //提交按钮统一使用 lay-filter="submit"
    //表单id统一使用 form
    form.on('submit(submit)', function (data) {
        let formData = new FormData(document.forms['form']);
        $.ajax({
            url: url,
            method: data.field.id ? 'PUT' : 'POST',
            data: formData,
            processData: false,
            contentType: false,
            dataType: 'json',
            success: function (resp) {
                if (resp.code === 0) {
                    table.reload('table', dic);
                    layer.msg(resp.msg, {icon: 1});
                    layer.close(model);
                } else {
                    layer.msg(resp.msg, {icon: 2});
                }
            },
            error: function (resp) {
                console.log(resp)
            }
        });
        return false;
    });

    //表单id统一使用 form
    $(document).on('click', '#add-btn', function () {
        document.forms['form'].reset();
        model = layer.open({
            type: 1,
            area: ['500px', 'auto'],
            title: '添加' + title,
            fixed: false,
            maxmin: true,
            content: $('#model'),
            success: function (layero, index) {
                $('#model').show();
            },
            cancel: function (layero, index) {
                $('#model').hide();
            }
        });
    });

    $(document).on('click', '#del-btn', function () {
        let id_str = checked_ids(table);
        layer.confirm('是否删除选中' + title + '？', {
            btn: ['确定', '取消'] //按钮
        }, function () {
            $.ajax({
                url: url,
                method: 'DELETE',
                data: {'ids': id_str},
                success: function (resp) {
                    if (resp.code === 0) {
                        table.reload('table', dic);
                        layer.msg(resp.msg, {icon: 1});
                    } else {
                        layer.msg(resp.msg, {icon: 2});
                    }
                },
                error: function () {

                },

            });
        }, function () {
        });
    });

    table.on('checkbox()', function (obj) {
        update_button($, table);
    });

    $(document).on('click', '.edit-btn', function (e) {
        var item = $(this).data('item');
        model = layer.open({
            type: 1,
            area: ['500px', 'auto'],
            title: '编辑' + title,
            fixed: false,
            maxmin: true,
            content: $('#model'),
            success: function (layero, index) {
                for (let k in item) {
                    $('#model [name="' + k + '"]').val(item[k]);
                }
                form.render('select');
                $('#model').show();
            },
            cancel: function (layero, index) {
                $('#model').hide();
            }
        });
    });

};