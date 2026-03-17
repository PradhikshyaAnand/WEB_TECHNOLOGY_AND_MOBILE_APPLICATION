package com.demo;

import java.io.IOException;
import java.io.PrintWriter;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

@WebServlet("/LoginServlet")
public class LoginServlet extends HttpServlet {

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/html");
        PrintWriter out = response.getWriter();

        String username = request.getParameter("username");
        String password = request.getParameter("password");

        if(username.equals("admin") && password.equals("1234")) {

            HttpSession session = request.getSession();
            session.setAttribute("username", username);

            out.println("<h2>Login Successful</h2>");
            out.println("Welcome " + username);
            out.println("<br><br>");
            out.println("<a href='LogoutServlet'>Logout</a>");

        } else {

            out.println("<h3>Invalid Username or Password</h3>");
            out.println("<a href='login.html'>Try Again</a>");
        }
    }
}