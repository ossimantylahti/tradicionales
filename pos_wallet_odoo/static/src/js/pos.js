// pos_wallet_odoo js
//console.log("custom callleddddddddddddddddddddd")
odoo.define('pos_wallet_odoo.pos', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var rpc = require('web.rpc');

    var QWeb = core.qweb;
	var _t = core._t;


    //
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'res.partner'; });
            partner_model.fields.push('wallet_balance');


            var journal_model = _.find(this.models, function(model){ return model.model === 'account.journal'; });
            journal_model.fields.push('wallet');
                        
            return _super_posmodel.initialize.call(this, session, attributes);
            
        },
        push_order: function(order, opts){
            var self = this;
            var pushed = _super_posmodel.push_order.call(this, order, opts);
            var client = order && order.get_client();
            
            if (client){
                order.paymentlines.each(function(line){
                    var journal = line.cashregister.journal;
            
                    var amount = line.get_amount();
                    
                    if (journal['wallet'] === true){
                    if (amount <= client.wallet_balance){
                      var updated = client.wallet_balance - amount;
                      
		                rpc.query({
		                    model: 'res.partner',
		                    method: 'write',
		                    args: [[client.id], {'wallet_balance': updated}],
		                });
                    
                    }
                    else{
                    }
                   }
                });
            }
            return pushed;
        }
    });


	// ClientListScreenWidget start
	gui.Gui.prototype.screen_classes.filter(function(el) { return el.name == 'clientlist'})[0].widget.include({
		
		display_client_details: function(visibility,partner,clickpos){
            var self = this;
            var contents = this.$('.client-details-contents');
            var parent   = this.$('.client-list').parent();
            var scroll   = parent.scrollTop();
            var height   = contents.height();

            contents.off('click','.button.edit');
            contents.off('click','.button.save');
            contents.off('click','.button.undo');
            contents.on('click','.button.edit',function(){ self.edit_client_details(partner); });
            contents.on('click','.button.save',function(){ self.save_client_details(partner); });
            contents.on('click','.button.undo',function(){ self.undo_client_details(partner); });
            this.editing_client = false;
            this.uploaded_picture = null;

            if(visibility === 'show'){
                contents.empty();
                contents.append($(QWeb.render('ClientDetails',{widget:this,partner:partner})));

                var new_height   = contents.height();

                if(!this.details_visible){
                    if(clickpos < scroll + new_height + 20 ){
                        parent.scrollTop( clickpos - 20 );
                    }else{
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                }else{
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }

                this.details_visible = true;
                
                // Click on Button, Open Popup pos-wallet Here...
                contents.on('click','.button.pos-wallet',function(){
            		self.gui.show_popup('pos_wallet_popup_widget', { 'partner': partner });

            	});
            	// End Custom Code...
            	
            	
                this.toggle_save_button();
            } else if (visibility === 'edit') {
                this.editing_client = true;
                contents.empty();
                contents.append($(QWeb.render('ClientDetailsEdit',{widget:this,partner:partner})));
                this.toggle_save_button();

                contents.find('.image-uploader').on('change',function(){
                    self.load_image_file(event.target.files[0],function(res){
                        if (res) {
                            contents.find('.client-picture img, .client-picture .fa').remove();
                            contents.find('.client-picture').append("<img src='"+res+"'>");
                            contents.find('.detail.picture').remove();
                            self.uploaded_picture = res;
                        }
                    });
                });
            } else if (visibility === 'hide') {
                contents.empty();
                if( height > scroll ){
                    contents.css({height:height+'px'});
                    contents.animate({height:0},400,function(){
                        contents.css({height:''});
                    });
                }else{
                    parent.scrollTop( parent.scrollTop() - height);
                }
                this.details_visible = false;
                this.toggle_save_button();
            }
        },
        close: function(){
            this._super();
        },
	});


    // PosWalletPopupWidget Popup start

    var PosWalletPopupWidget = popups.extend({
        template: 'PosWalletPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        
        show: function(options) {
            this._super(options);
            this.partner = options.partner || [];
            this.renderElement();

        },
        
        renderElement: function() {
            var self = this;
            this._super();
            var partner_id = this.partner;
            
            this.$('#add_wallet_money').click(function() {
                var entered_amount = $("#wallet_amount").val();
                
                var payment_type = $('#payment_type').val();
                
                
                rpc.query({
			        model: 'pos.wallet.transaction',
			        method: 'wallet_recharge',
			        args: [partner_id ? partner_id.id : 0, partner_id, entered_amount, payment_type],
	            
	            }).then(function(output) {
                    
					alert('Wallet successfully recharged');	
                    self.gui.show_screen('clientlist');
                    //===========================================================================
                    //screens.reload_partners();
                    //self.pos.screens.display_client_details();
                    self.chrome.screens.clientlist.saved_client_details(partner_id);
                    //self.gui.show_screen(refresh);
                    //console.log('ccccccccccccccccccccccccccccccccccccccccccccccccccccccc',partner_id)
                    //===========================================================================

                });
            });
        },

    });
    gui.define_popup({
        name: 'pos_wallet_popup_widget',
        widget: PosWalletPopupWidget
    });

    // End Popup start



  // PaymentScreenWidget start
  screens.PaymentScreenWidget.include({
        validate_order: function(options) {
            var currentOrder = this.pos.get_order();
            
            var plines = currentOrder.get_paymentlines();
            
            var dued = currentOrder.get_due();
            
            var changed = currentOrder.get_change();
            
            var clients = currentOrder.get_client();
            
            if (clients){  //if customer is selected
		        for (var i = 0; i < plines.length; i++) {
		           if (plines[i].cashregister.journal['type'] === "cash" && plines[i].cashregister.journal['wallet'] === true) { //we've given cash Type
				       if(plines[i]['amount'] > clients.wallet_balance){ // Make Condition that amount is greater than selected customer's wallet amount
						   this.gui.show_popup('error',{
						        'title': _t('Not Sufficient Wallet Balance'),
						        'body': _t('Customer has not Sufficient Wallet Balance To Pay'),
						    });
						    return;
				    }
				  }
		        } 
			}
			
		        for (var i = 0; i < plines.length; i++) {

		           	 if (plines[i].cashregister.journal['wallet'] === true){
					  
				       if(currentOrder.get_change() > 0){ // Make Condition that amount is greater than selected customer's wallet amount
						   this.gui.show_popup('error',{
				            'title': _t('Payment Amount Exceeded'),
				            'body': _t('You cannot Pay More than Total Amount'),
				        });
                		return;
				    }
				    
				    // Make Condition: Popup Occurs When Customer is not selected on wallet payment method, While any other payment method, this error popup will not be showing
				    if (!currentOrder.get_client()){
				        this.gui.show_popup('error',{
				            'title': _t('Unknown customer'),
				            'body': _t('You cannot use Wallet payment. Select customer first.'),
				        });
				        return;
				    }
				    
				  }
		        } //}

            if(currentOrder.get_orderlines().length === 0){
                this.gui.show_popup('error',{
                    'title': _t('Empty Order'),
                    'body': _t('There must be at least one product in your order before it can be validated.'),
                });
                return;
            }

            this._super(options);
        },


     
    });
    
        
    

});
