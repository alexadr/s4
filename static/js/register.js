'use strict';

angular.module('register',[]);

angular.module('register').
    component('register', {
        templateUrl: '/static/html/register-detail.html',
        controller: function(
                $cookies, 
                $http, 
                $location, 
                $routeParams, 
                $rootScope, 
                $scope
            ){
            var registerUrl = '/rest-auth/registration/';
            $scope.registerError = {};
            $scope.user = {

            };



            var tokenExists = $cookies.get("token");
            if (tokenExists) {
                // warn user
                
            }

            $scope.doRegister = function(user){
                // console.log(user)
                if (!user.username) {
                    $scope.registerError.username = ["This field may not be blank."]
                } 
                if (!user.email) {
                    $scope.registerError.email = ["This field may not be blank."]
                } 

                if (!user.email2) {
                    $scope.registerError.email2 = ["This field may not be blank."]
                } 

                if (user.email && user.email != user.email2) {
                    $scope.registerError.email = ["Your emails must match."]
                }


                if (!user.password1) {
                    $scope.registerError.password1 = ["This field is required."]
                }
                if (!user.password2) {
                    $scope.registerError.password2 = ["This field is required."]
                }

                 if (user.password1 && user.password1 != user.password2) {
                    $scope.registerError.password1 = ["Your password must match."]
                }

                if (user.username && user.email && user.email2 && user.password1&& user.password2) {
                    var reqConfig = {
                        method: "POST",
                        url: registerUrl,
                        data: {
                            username: user.username,
                            email: user.email,
                            email2: user.email2,
                            password1: user.password1,
                            password2: user.password2
                        },
                            headers: {}
                    };
                    var requestAction = $http(reqConfig);
                    
                    requestAction.success(function(r_data, r_status, r_headers, r_config){
                            // console.log(r_data) // token
                            $cookies.put("token", r_data.key);
                            $cookies.put("username", user.username);
                            // message
                            $location.path("/");
                    });
                    requestAction.error(function(e_data, e_status, e_headers, e_config){
                            // console.log(e_data) // error
                            $scope.registerError = e_data

                    })
                }
                

            };
            // $http.post()
        }
});
