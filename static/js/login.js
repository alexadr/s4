'use strict';

angular.module('login', []);

angular.module('login').component('login', {
    templateUrl: 'static/html/login.html',
    controller: function ($cookies,
                          $http,
                          $location,
                          $routeParams,
                          $rootScope,
                          $scope) {
        var loginUrl = '/rest-auth/login/';
        $scope.loginError = {};
        $scope.user = {};

        $scope.$watch(function () {
            if ($scope.user.password) {
                $scope.loginError.password = ""
            } else if ($scope.user.username) {
                $scope.loginError.username = ""
            }
        });

        var tokenExists = $cookies.get("token");
        if (tokenExists) {
            // verify token
            $scope.loggedIn = true;
            $cookies.remove("token");
            $scope.user = {
                username: $cookies.get("username")
            };
            window.location.reload()
        }

        $scope.doLogin = function (user) {
            // console.log(user)
            if (!user.username) {
                $scope.loginError.username = ["This field may not be blank."]
            }

            if (!user.password) {
                $scope.loginError.password = ["This field is required."]
            }

            if (user.username && user.password) {
                var reqConfig = {
                    method: "POST",
                    url: loginUrl,
                    data: {
                        'username': user.username,
                        'password': user.password,
                        'next': "/"
                    }
                    //headers: {'Content-Type':  "application/x-www-form-urlencoded" }
                };
                var requestAction = $http(reqConfig);

                requestAction.success(function (r_data, r_status, r_headers, r_config) {
                    // console.log(r_data) // token

                    $http.defaults.headers.common.Authorization = 'Token ' + r_data.key;
                    $cookies.put('token', r_data.key);
                    //$cookieStore.put('djangotoken', response.token);
                    //$cookies.put("token", r_data.token)
                    $cookies.put("username", user.username);
                    // message
                    $location.path("/account/");
                    //window.location.reload()
                });
                requestAction.error(function (e_data, e_status, e_headers, e_config) {
                    // console.log(e_data) // error
                    $scope.loginError = e_data

                })
            }
        };
    }
});
