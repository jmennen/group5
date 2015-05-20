(function() {
  var app = angular.module('searchList', []);

  app.controller('PersonController', function(){
    this.persons = users;
  });

  var users = [
    { name: 'Azurite', description: 2.95 , gender: 'male'},
    { name: 'Bloodstone', description: 5.95  , gender: 'male'},
    { name: 'Zircon', description: 3.95  , gender: 'male'}
  ];
})();