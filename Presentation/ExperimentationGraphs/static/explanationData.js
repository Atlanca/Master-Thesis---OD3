ontologyData = {"entities": [{"uri": "http://www.semanticweb.org/ontologies/snowflake#purchase_products", "label": "Purchase products", "type": "http://www.semanticweb.org/ontologies/snowflake#Feature", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#Feature"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Description", "Figure 3.4 shows the use cases related to purchasing products. They can be clearly divided into two different topics: on the one hand all those use cases for managing the shopping cart (i.e. adding, updating and removing items), on the other hand those related to placing and listing orders. When placing an order the customer may be requested to pay online, in which case the payment platform will provide the necessary means. Anonymous as much as registered customers can place orders, but only customers that have been identified are able to list their own orders, otherwise they are requested to identify themselves."]], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_3.4_purchase_products"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#add_item_to_cart", "label": "Add item to cart", "type": "http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "http://www.semanticweb.org/ontologies/snowflake#Requirement"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Description", "As a customer, I want to add a particular product to the shopping cart, so that I can buy it with the next order."], ["http://www.semanticweb.org/ontologies/snowflake#Priority", "1"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Cart", "label": "Cart", "type": "http://www.semanticweb.org/ontologies/snowflake#LogicalClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#LogicalClass", "http://www.semanticweb.org/ontologies/snowflake#LogicalClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Logical", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment", "http://www.semanticweb.org/ontologies/snowflake#LogicalStructure"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_3.10_class_diagram_of_the_system"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_Carts", "label": "Carts.java", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.39_web_application_server_contoller_component", "http://www.semanticweb.org/ontologies/snowflake#figure_4.25_internal_design_browse_catalog"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_Carts.java", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "git\\sphere-snowflake\\app\\controllers\\Carts.java"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Client_Controller_Cart", "label": "Cart.js", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.40_client_controller_component", "http://www.semanticweb.org/ontologies/snowflake#figure_4.27_internal_design_checkout_cart_update_detail", "http://www.semanticweb.org/ontologies/snowflake#figure_4.25_internal_design_browse_catalog"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_carts.scala", "label": "carts.scala", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.36_web_application_server_view_component", "http://www.semanticweb.org/ontologies/snowflake#figure_4.27_internal_design_checkout_cart_update_detail"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_carts.scala.html", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "views/carts.scala.html"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_CartNoEmpty", "label": "CartNoEmpty.java", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.39_web_application_server_contoller_component"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_CartNotEmpty.java", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "controllers.actions.CartNotEmpty"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_CartForms", "label": "Carts", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassPackage", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassPackage", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.34_web_application_server_form_model_component"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_RemoveFromCart", "label": "RemoveFromCart", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.34_web_application_server_form_model_component"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_RemoveFromCart.java", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "git\\sphere-snowflake\\app\\forms\\cartForm\\RemoveFromCart.java"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_UpdateCart", "label": "UpdateCart", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.34_web_application_server_form_model_component"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_UpdateCart.java", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "git\\sphere-snowflake\\app\\forms\\cartForm\\UpdateCart.java"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_ManageCart", "label": "ManageCart", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.34_web_application_server_form_model_component"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_ListCart.java", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "git\\sphere-snowflake\\app\\forms\\cartForm\\ListCart.java"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_AddToCart", "label": "AddToCart", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.34_web_application_server_form_model_component"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_AddToCart.java", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "git\\sphere-snowflake\\app\\forms\\cartForm\\AddToCart.java"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#place_order", "label": "Place order", "type": "http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "http://www.semanticweb.org/ontologies/snowflake#Requirement"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Description", "As a customer, I want to place an order, so that I can actually buy the items in my shopping cart."], ["http://www.semanticweb.org/ontologies/snowflake#Priority", "2"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Order", "label": "Order", "type": "http://www.semanticweb.org/ontologies/snowflake#LogicalClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#LogicalClass", "http://www.semanticweb.org/ontologies/snowflake#LogicalClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Logical", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment", "http://www.semanticweb.org/ontologies/snowflake#LogicalStructure"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_3.10_class_diagram_of_the_system"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orders.scala", "label": "orders.scala", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.36_web_application_server_view_component", "http://www.semanticweb.org/ontologies/snowflake#figure_4.30_internal_design_checkout_order_creation"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orders.scala.html", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "views/orders.scala.html"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_order.scala", "label": "order.scala", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.37_web_application_server_simple_views"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_order.scala.html", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "views/helper/order.scala.html"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderSummary.scala", "label": "orderSummary.scala", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.37_web_application_server_simple_views"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderSummary.scala.html", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "views/helper/orderSummary.scala.html"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderList.scala", "label": "orderList.scala", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.37_web_application_server_simple_views"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderList.scala.html", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "views/helper/orderList.scala.html"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Client_View_order-summary-template", "label": "order-summary-template", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#figure_4.38_client_side_view_component"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Client_Model_OrderSummary", "label": "OrderSummary", "type": "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#DevelopmentClass", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentClassFragment", "http://www.semanticweb.org/ontologies/snowflake#Development", "http://www.semanticweb.org/ontologies/snowflake#DevelopmentStructure", "http://www.semanticweb.org/ontologies/snowflake#ArchitectureFragment"], "dataTypeProperties": [], "diagrams": ["http://www.semanticweb.org/ontologies/snowflake#Figure_4.35_client_side_model_component"]}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#Client_Model_order-summary.coffee", "label": "", "type": "http://www.semanticweb.org/ontologies/snowflake#ImplementationClass", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#ImplementationClass"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Path", "assets/javascripts/demo/order-summary.coffee"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#remove_item_from_cart", "label": "Remove item from cart", "type": "http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "http://www.semanticweb.org/ontologies/snowflake#Requirement"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Description", "As a customer, I want to remove a particular item from the shopping cart, so that I do not buy it with the next order"], ["http://www.semanticweb.org/ontologies/snowflake#Priority", "3"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#payment", "label": "Payment", "type": "http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "http://www.semanticweb.org/ontologies/snowflake#Requirement"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Description", "As a customer, I want to be able to pay online my orders, so that I can pay immediately the moment I buy them instead of using other possibly unpleasant billing options."], ["http://www.semanticweb.org/ontologies/snowflake#Priority", "4"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#list_orders", "label": "List orders", "type": "http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "http://www.semanticweb.org/ontologies/snowflake#Requirement"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Description", "As a registered customer, I want to see a list of my orders, so that I can see all the purchases I did in the past."], ["http://www.semanticweb.org/ontologies/snowflake#Priority", "5"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#mini_cart", "label": "Mini cart", "type": "http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "http://www.semanticweb.org/ontologies/snowflake#Requirement"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Description", "As a customer, I want to be able to see my current shopping cart from any page via a so-called mini-cart, so that I can always be aware of its contents and pricing details."], ["http://www.semanticweb.org/ontologies/snowflake#Priority", "5"]], "diagrams": []}, {"uri": "http://www.semanticweb.org/ontologies/snowflake#update_item_in_cart", "label": "Update item in cart", "type": "http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "supertypes": ["http://www.semanticweb.org/ontologies/snowflake#FunctionalRequirement", "http://www.semanticweb.org/ontologies/snowflake#Requirement"], "dataTypeProperties": [["http://www.semanticweb.org/ontologies/snowflake#Description", "As a customer, I want to change the number of units of a particular item in the shopping cart, so that I can buy a different quantity of the product with the next order"], ["http://www.semanticweb.org/ontologies/snowflake#Priority", "6"]], "diagrams": []}], "relations": [{"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#purchase_products", "target": "http://www.semanticweb.org/ontologies/snowflake#add_item_to_cart"}, {"name": "satisfiedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#add_item_to_cart", "target": "http://www.semanticweb.org/ontologies/snowflake#Cart"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Cart", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_Carts"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_Carts", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_Carts.java"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Cart", "target": "http://www.semanticweb.org/ontologies/snowflake#Client_Controller_Cart"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Cart", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_carts.scala"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_View_carts.scala", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_carts.scala.html"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Cart", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_CartNoEmpty"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_CartNoEmpty", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Controller_CartNotEmpty.java"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Cart", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_CartForms"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_CartForms", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_RemoveFromCart"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_RemoveFromCart", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_RemoveFromCart.java"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_CartForms", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_UpdateCart"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_UpdateCart", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_UpdateCart.java"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_CartForms", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_ManageCart"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_ManageCart", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_ListCart.java"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_CartForms", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_AddToCart"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_AddToCart", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_Model_AddToCart.java"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#purchase_products", "target": "http://www.semanticweb.org/ontologies/snowflake#place_order"}, {"name": "satisfiedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#place_order", "target": "http://www.semanticweb.org/ontologies/snowflake#Order"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Order", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orders.scala"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orders.scala", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orders.scala.html"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Order", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_order.scala"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_View_order.scala", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_order.scala.html"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Order", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderSummary.scala"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderSummary.scala", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderSummary.scala.html"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Order", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderList.scala"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderList.scala", "target": "http://www.semanticweb.org/ontologies/snowflake#Server_View_orderList.scala.html"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Order", "target": "http://www.semanticweb.org/ontologies/snowflake#Client_View_order-summary-template"}, {"name": "designedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Order", "target": "http://www.semanticweb.org/ontologies/snowflake#Client_Model_OrderSummary"}, {"name": "implementedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#Client_Model_OrderSummary", "target": "http://www.semanticweb.org/ontologies/snowflake#Client_Model_order-summary.coffee"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#purchase_products", "target": "http://www.semanticweb.org/ontologies/snowflake#remove_item_from_cart"}, {"name": "satisfiedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#remove_item_from_cart", "target": "http://www.semanticweb.org/ontologies/snowflake#Cart"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#purchase_products", "target": "http://www.semanticweb.org/ontologies/snowflake#payment"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#purchase_products", "target": "http://www.semanticweb.org/ontologies/snowflake#list_orders"}, {"name": "satisfiedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#list_orders", "target": "http://www.semanticweb.org/ontologies/snowflake#Order"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#purchase_products", "target": "http://www.semanticweb.org/ontologies/snowflake#mini_cart"}, {"name": "satisfiedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#mini_cart", "target": "http://www.semanticweb.org/ontologies/snowflake#Cart"}, {"name": "compriseOf", "source": "http://www.semanticweb.org/ontologies/snowflake#purchase_products", "target": "http://www.semanticweb.org/ontologies/snowflake#update_item_in_cart"}, {"name": "satisfiedBy", "source": "http://www.semanticweb.org/ontologies/snowflake#update_item_in_cart", "target": "http://www.semanticweb.org/ontologies/snowflake#Cart"}]}