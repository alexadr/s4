'use strict';

var na = angular.module('navigation',[]);

na.
  directive('navigation', function($cookies){
    return {    
        restrict: "E",
        templateUrl: "/static/html/navigation.html",
        link: function (scope, element, attr) {

            scope.userLoggedIn = false;
            scope.$watch(function(){
                var token = $cookies.get("token");
                if (token) {
                    scope.userLoggedIn = true
                } else {
                    scope.userLoggedIn = false
                }

                var user = $cookies.get("username");
                if (user) {
                    scope.user = user
                } else {
                    scope.user = user
                }
            })
            

        }
    }
});