import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.WebServlet;

@WebServlet("/FormServlet")

public class FormServlet extends HttpServlet {

 protected void doPost(HttpServletRequest request, HttpServletResponse response)
 throws ServletException, IOException {

  response.setContentType("text/html");
  PrintWriter out = response.getWriter();

  String name = request.getParameter("name");
  String age = request.getParameter("age");

  out.println("<html><body>");
  out.println("<h2>Hello " + name + "! You are " + age + " years old.</h2>");
  out.println("</body></html>");
 }
}