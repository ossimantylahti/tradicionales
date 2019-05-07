odoo.define('sun_pos_advance_note.addnote', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var PopupWidget = require('point_of_sale.popups');
var core = require('web.core');

var QWeb = core.qweb;

    var AddNoteButton = screens.ActionButtonWidget.extend({
        template: 'AddNoteButton',
        button_click: function(){
            var order    = this.pos.get_order();
            var lines    = order.get_orderlines();
            if(lines.length > 0) {
                var selected_line = order.get_selected_orderline();
                if (selected_line) {
                	this.gui.show_popup('add_note_popup');
                }
            } else {
                alert("Please select the product !");
            }
        },
    });

    screens.define_action_button({
        'name': 'addnoteline',
        'widget': AddNoteButton,
        'condition': function(){
            return this.pos.config.enable_product_note;
        },
    });

    var ProductNotePopupWidget = PopupWidget.extend({
	    template: 'ProductNotePopupWidget',
	    show: function(options){
	        options = options || {};
	        this._super(options);
	
	        this.renderElement();
	        var order    = this.pos.get_order();
	    	var selected_line = order.get_selected_orderline();
	    	$('textarea#textarea_note').focus();
	        $('textarea#textarea_note').html(selected_line.get_line_note());
	    },
	    click_confirm: function(){
	    	var order    = this.pos.get_order();
	    	var selected_line = order.get_selected_orderline();
	    	var value = this.$('#textarea_note').val();
	    	selected_line.set_line_note(value);
	    	this.gui.close_popup();
	    },
	    renderElement: function() {
            var self = this;
            this._super();
    	},
	    
	});
	gui.define_popup({name:'add_note_popup', widget: ProductNotePopupWidget});
    
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
    	
        initialize: function(attr,options){
            this.line_note = '';
            _super_orderline.initialize.call(this, attr, options);
        },
        set_line_note: function(line_note) {
            this.set('line_note', line_note);
        },
        get_line_note: function() {
            return this.get('line_note');
        },
        export_as_JSON: function() {
            var lines = _super_orderline.export_as_JSON.call(this);
            var new_attr = {
                line_note: this.get_line_note(),
            }
            $.extend(lines, new_attr);
            return lines;
        },
        export_for_printing: function() {
        	var self = this;
        	self.pos.product_note = self.pos.config.is_productnote_receipt;
            var lines = _super_orderline.export_for_printing.call(this);
            var new_attr = {
                line_note: this.get_line_note(),
            }
            $.extend(lines, new_attr);
            return lines;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
    	
        set_order_note: function(order_note) {
            this.order_note = order_note;
        },
        get_order_note: function() {
            return this.order_note;
        },
        export_as_JSON: function() {
            var submitted_order = _super_order.export_as_JSON.call(this);
            var new_val = {
                order_note: this.get_order_note(),
            }
            $.extend(submitted_order, new_val);
            return submitted_order;
        },
        export_for_printing: function(){
        	var self = this;
        	self.pos.order_note = self.pos.config.is_ordernote_receipt;
            var orders = _super_order.export_for_printing.call(this);
            var new_val = {
            	order_note: this.get_order_note() || false,
            };
            $.extend(orders, new_val);
            return orders;
        },
    });

    screens.PaymentScreenWidget.include({
        show: function() {
            self = this;
            this._super();
            $("textarea#order_note").focus(function() {
            	 $('body').off('keypress', self.keyboard_handler);
                 $('body').off('keydown', self.keyboard_keydown_handler);
                 window.document.body.removeEventListener('keypress',self.keyboard_handler);
                 window.document.body.removeEventListener('keydown',self.keyboard_keydown_handler);
            });
            $("textarea#order_note").focusout(function() {
            	window.document.body.addEventListener('keypress',self.keyboard_handler);
                window.document.body.addEventListener('keydown',self.keyboard_keydown_handler);
            });
        },
        validate_order: function(force_validation) {
            if(this.pos.config.enable_order_note) {
                var currentOrder = this.pos.get_order();
                currentOrder.set_order_note($('#order_note').val());
            }
            this._super(force_validation);
        },
    });

});