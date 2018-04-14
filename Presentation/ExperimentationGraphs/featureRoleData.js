featureRoleData = {"Feature": [[null, {"type": "Feature", "object": "purchase_products", "dataTypeProperties": [["Description", "Figure 3.4 shows the use cases related to purchasing products. They can be clearly divided into two different topics: on the one hand all those use cases for managing the shopping cart (i.e. adding, updating and removing items), on the other hand those related to placing and listing orders. When placing an order the customer may be requested to pay online, in which case the payment platform will provide the necessary means. Anonymous as much as registered customers can place orders, but only customers that have been identified are able to list their own orders, otherwise they are requested to identify themselves."]]}]], "Requirement": [["compriseOf", {"type": "FunctionalRequirement", "object": "add_item_to_cart", "dataTypeProperties": [["Priority", "1"], ["Description", "As a customer, I want to add a particular product to the shopping cart, so that I can buy it with the next order."]]}], ["compriseOf", {"type": "FunctionalRequirement", "object": "update_item_in_cart", "dataTypeProperties": [["Priority", "6"], ["Description", "As a customer, I want to change the number of units of a particular item in the shopping cart, so that I can buy a different quantity of the product with the next order"]]}], ["compriseOf", {"type": "FunctionalRequirement", "object": "mini_cart", "dataTypeProperties": [["Priority", "5"], ["Description", "As a customer, I want to be able to see my current shopping cart from any page via a so-called mini-cart, so that I can always be aware of its contents and pricing details."]]}], ["compriseOf", {"type": "FunctionalRequirement", "object": "payment", "dataTypeProperties": [["Priority", "4"], ["Description", "As a customer, I want to be able to pay online my orders, so that I can pay immediately the moment I buy them instead of using other possibly unpleasant billing options."]]}], ["compriseOf", {"type": "FunctionalRequirement", "object": "place_order", "dataTypeProperties": [["Priority", "2"], ["Description", "As a customer, I want to place an order, so that I can actually buy the items in my shopping cart."]]}], ["compriseOf", {"type": "FunctionalRequirement", "object": "list_orders", "dataTypeProperties": [["Priority", "5"], ["Description", "As a registered customer, I want to see a list of my orders, so that I can see all the purchases I did in the past."]]}], ["compriseOf", {"type": "FunctionalRequirement", "object": "remove_item_from_cart", "dataTypeProperties": [["Priority", "3"], ["Description", "As a customer, I want to remove a particular item from the shopping cart, so that I do not buy it with the next order"]]}]], "UseCase": [["partOf", {"type": "UseCase", "object": "browse_catalog", "dataTypeProperties": [["Description", "Figure 3.7 displays the sequence diagram for the browse catalog top-level use case, one of the many possible success scenarios. In this case the user will usually go to the home page, select a 40 category and then filter or sort the products until he eventually finds one of interest. Then he will probably ask for the details of the product and next he will add it to the shopping cart."]]}]], "Diagram": [["modeledIn", {"type": "Diagram", "object": "figure_3.4_purchase_products", "dataTypeProperties": [["Description", "Use case diagram showing the use cases of the purchase products package."]]}]]}; relImpClassesData = [[null, {"type": "Feature", "object": "purchase_products", "implClasses": [], "children": [["realizedBy", {"type": "ClassPackage", "object": "CartForms", "implClasses": [], "children": []}], ["realizedBy", {"type": "ClassPackage", "object": "PaymentForms", "implClasses": [], "children": []}]]}]]; architectureData = [["playsRole", {"type": "Role", "object": "server_model_1", "dataTypeProperties": [], "children": [["roleImplementedBy", {"type": "Package", "object": "web_application_server_model_package_1", "dataTypeProperties": [], "children": [["compriseOf", {"type": "ClassEntity", "object": "ViewHelper", "dataTypeProperties": [["Description", "On the other hand, the View Helper is a common design pattern that allows to separate logic that otherwise needs to be integrated in the template, in this project applied with the ViewHelper class. Although templates in Play Framework enables to use all the potential of the programming language Scala, it is a good practice to keep complex logic out of the templates. All this logic is then placed in these helper classes and called from the views as necessary."]], "children": []}], ["compriseOf", {"type": "ClassPackage", "object": "Forms", "dataTypeProperties": [["Description", "Lastly, there are a group of classes related to the web forms and the payment information received by the system (see Figure 4.34). They handle all the server-side validation for every parameter and may also provide helpful getters and setters to easily convert model data into form data, and vice versa (e.g. an Address class instance would be converted into the appropriate form fields street, city, country, etc.)\n\nThese form classes also host the methods generating the different content that must be sent back to the client in relation to the result of the form submission. For example, when updating a line item from the cart, a success response contains a message for the user and all the shopping cart related information. This related information is generated with some other methods located in the forms as well, that convert a model class instance into JSON data."]], "children": [["compriseOf", {"type": "ClassPackage", "object": "AddressForms", "dataTypeProperties": [], "children": []}], ["compriseOf", {"type": "ClassPackage", "object": "CartForms", "dataTypeProperties": [], "children": []}], ["compriseOf", {"type": "ClassPackage", "object": "PaymentForms", "dataTypeProperties": [], "children": []}], ["compriseOf", {"type": "ClassPackage", "object": "PasswordForms", "dataTypeProperties": [], "children": []}], ["compriseOf", {"type": "ClassPackage", "object": "CustomerForms", "dataTypeProperties": [], "children": []}]]}], ["compriseOf", {"type": "ClassEntity", "object": "Mail", "dataTypeProperties": [["Description", "The system also requires a class to send emails through any email system of preference. The Mail class will cover this functionality, as long as the SMTP17 details of the email system are provided. Given that Heroku does not provide an internal SMTP server, the deployed version of this project will need to use an external server like Mailjet, a cloud emailing platform that offers several features that may be of interest for potential clients."]], "children": []}], ["compriseOf", {"type": "ClassEntity", "object": "ControllerHelper", "dataTypeProperties": [["Description", "The Model component is also containing different helpers, where some particular logic of this web-shop is located. The ControllerHelper is composed of methods that allows to abstract some common logic that is used in the Controller component (i.e. logic to handle and display messages and errors) or data coming from SPHERE.IO requiring some previous manipulation before it is used (i.e. get default category of a product or get address book of the current customer)."]], "children": []}], ["compriseOf", {"type": "ClassEntity", "object": "Sphere", "dataTypeProperties": [["Description", "As described at the beginning of the section System Logical Architectural 4.2, the logic of the model component is largely located in the SPHERE.IO Play SDK, which contains all the commerce logic and allows to access all data stored in the e-commerce backend. The Sphere class shown in the diagram below (Figure 4.33) is precisely the entry point for SPHERE.IO."]], "children": []}], ["compriseOf", {"type": "ClassEntity", "object": "Payment", "dataTypeProperties": [["Description", "There is also a Payment class, a small library that will help to communicate with the Optile API, that requires the messages to be sent using XML. As explained before (see section 4.2.1.2), Optile needs to be implemented in an incremental way, reason why the library can effortless cover all five levels of integration, thus allowing developers to easily switch to the level it fits best for them."]], "children": []}]]}]]}]]